"""GraphQL Pagination Template for Ainflue Platform
Enterprise-grade GraphQL pagination with Relay cursor-based pagination

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
import base64
import json
from typing import Dict, Any, Optional, List, Union, Tuple, Generic, TypeVar
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

import graphene
from graphene import ObjectType, String, Int, Boolean, Field, List as GrapheneList
from graphene.relay import Connection, ConnectionField, PageInfo, Node
from sqlalchemy import asc, desc, and_, or_, func
from sqlalchemy.orm import Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.database import get_db_session
from core.auth import get_current_user
from core.logging import log_pagination_operation
from utils.exceptions import PaginationException
from monitoring.api_metrics import PaginationMetrics

logger = logging.getLogger(__name__)
settings = get_settings()

T = TypeVar('T')


class PaginationDirection(Enum):
    """Pagination direction"""
    FORWARD = "forward"
    BACKWARD = "backward"


class SortDirection(Enum):
    """Sort direction"""
    ASC = "asc"
    DESC = "desc"


@dataclass
class CursorInfo:
    """Cursor information for pagination"""
    value: Any
    field: str
    direction: SortDirection = SortDirection.ASC
    
    def encode(self) -> str:
        """Encode cursor to base64 string"""
        cursor_data = {
            "value": str(self.value),
            "field": self.field,
            "direction": self.direction.value
        }
        cursor_json = json.dumps(cursor_data, sort_keys=True)
        return base64.b64encode(cursor_json.encode()).decode()
    
    @classmethod
    def decode(cls, cursor: str) -> "CursorInfo":
        """Decode cursor from base64 string"""
        try:
            cursor_json = base64.b64decode(cursor.encode()).decode()
            cursor_data = json.loads(cursor_json)
            return cls(
                value=cursor_data["value"],
                field=cursor_data["field"],
                direction=SortDirection(cursor_data["direction"])
            )
        except Exception as e:
            logger.error(f"Error decoding cursor: {e}")
            raise PaginationException("Invalid cursor format")


@dataclass
class PaginationParams:
    """Pagination parameters"""
    first: Optional[int] = None
    after: Optional[str] = None
    last: Optional[int] = None
    before: Optional[str] = None
    sort_field: str = "id"
    sort_direction: SortDirection = SortDirection.ASC
    
    def validate(self):
        """Validate pagination parameters"""
        if self.first is not None and self.last is not None:
            raise PaginationException("Cannot specify both 'first' and 'last'")
        
        if self.after is not None and self.before is not None:
            raise PaginationException("Cannot specify both 'after' and 'before'")
        
        if self.first is not None and self.first <= 0:
            raise PaginationException("'first' must be positive")
        
        if self.last is not None and self.last <= 0:
            raise PaginationException("'last' must be positive")
        
        # Limit page size to prevent abuse
        max_page_size = 100
        if self.first and self.first > max_page_size:
            self.first = max_page_size
        if self.last and self.last > max_page_size:
            self.last = max_page_size
    
    @property
    def is_forward_pagination(self) -> bool:
        """Check if this is forward pagination"""
        return self.first is not None or self.after is not None
    
    @property
    def is_backward_pagination(self) -> bool:
        """Check if this is backward pagination"""
        return self.last is not None or self.before is not None


class CursorPaginator:
    """Cursor-based paginator for GraphQL connections"""
    
    def __init__(self, model_class, session: AsyncSession):
        self.model_class = model_class
        self.session = session
        self.metrics = PaginationMetrics()
    
    async def paginate(
        self,
        query: Query,
        params: PaginationParams
    ) -> Dict[str, Any]:
        """Paginate query with cursor-based pagination"""
        
        params.validate()
        
        # Apply sorting
        sort_column = getattr(self.model_class, params.sort_field)
        if params.sort_direction == SortDirection.ASC:
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        
        # Apply cursor filtering
        if params.after:
            cursor_info = CursorInfo.decode(params.after)
            query = self._apply_after_cursor(query, cursor_info)
        
        if params.before:
            cursor_info = CursorInfo.decode(params.before)
            query = self._apply_before_cursor(query, cursor_info)
        
        # Determine page size and direction
        if params.is_forward_pagination:
            limit = params.first or 20
            # Get one extra item to check if there's a next page
            items = await self._execute_query(query.limit(limit + 1))
            has_next_page = len(items) > limit
            if has_next_page:
                items = items[:-1]
            has_previous_page = params.after is not None
            
        else:  # Backward pagination
            limit = params.last or 20
            # For backward pagination, we need to reverse the order temporarily
            items = await self._execute_query(query.limit(limit + 1))
            has_previous_page = len(items) > limit
            if has_previous_page:
                items = items[:-1]
            items = list(reversed(items))  # Reverse to correct order
            has_next_page = params.before is not None
        
        # Create edges with cursors
        edges = []
        for item in items:
            cursor_info = CursorInfo(
                value=getattr(item, params.sort_field),
                field=params.sort_field,
                direction=params.sort_direction
            )
            edges.append({
                "node": item,
                "cursor": cursor_info.encode()
            })
        
        # Create page info
        page_info = {
            "has_next_page": has_next_page,
            "has_previous_page": has_previous_page,
            "start_cursor": edges[0]["cursor"] if edges else None,
            "end_cursor": edges[-1]["cursor"] if edges else None
        }
        
        # Record metrics
        self.metrics.record_pagination(
            model_name=self.model_class.__name__,
            page_size=len(edges),
            direction="forward" if params.is_forward_pagination else "backward"
        )
        
        return {
            "edges": edges,
            "page_info": page_info,
            "total_count": await self._get_total_count(query)
        }
    
    def _apply_after_cursor(self, query: Query, cursor_info: CursorInfo) -> Query:
        """Apply after cursor filter"""
        sort_column = getattr(self.model_class, cursor_info.field)
        
        if cursor_info.direction == SortDirection.ASC:
            return query.filter(sort_column > cursor_info.value)
        else:
            return query.filter(sort_column < cursor_info.value)
    
    def _apply_before_cursor(self, query: Query, cursor_info: CursorInfo) -> Query:
        """Apply before cursor filter"""
        sort_column = getattr(self.model_class, cursor_info.field)
        
        if cursor_info.direction == SortDirection.ASC:
            return query.filter(sort_column < cursor_info.value)
        else:
            return query.filter(sort_column > cursor_info.value)
    
    async def _execute_query(self, query: Query) -> List[Any]:
        """Execute query and return results"""
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def _get_total_count(self, base_query: Query) -> int:
        """Get total count for the query (without pagination)"""
        # Remove order by and limit clauses for count
        count_query = base_query.statement.with_only_columns([func.count()])
        result = await self.session.execute(count_query)
        return result.scalar()


class {{EntityName}}Edge(ObjectType):
    """Edge type for {{entity_description}} connection"""
    
    node = Field("{{EntityName}}Type", description="The {{entity_description}} at the end of the edge")
    cursor = String(required=True, description="Cursor for this edge")


class {{EntityName}}PageInfo(ObjectType):
    """Page info for {{entity_description}} connection"""
    
    has_next_page = Boolean(required=True, description="Whether there are more pages")
    has_previous_page = Boolean(required=True, description="Whether there are previous pages")
    start_cursor = String(description="Cursor of the first edge")
    end_cursor = String(description="Cursor of the last edge")


class {{EntityName}}Connection(ObjectType):
    """Connection for paginated {{entity_description}} results"""
    
    edges = GrapheneList({{EntityName}}Edge, description="List of edges")
    page_info = Field({{EntityName}}PageInfo, required=True, description="Pagination info")
    total_count = Int(description="Total number of items")
    
    def resolve_total_count(self, info):
        """Resolve total count"""
        return getattr(self, "_total_count", 0)


class PaginatedQuery:
    """Base class for paginated GraphQL queries"""
    
    @staticmethod
    async def resolve_paginated_list(
        info,
        model_class,
        base_query_func: callable,
        first: Optional[int] = None,
        after: Optional[str] = None,
        last: Optional[int] = None,
        before: Optional[str] = None,
        sort_field: str = "created_at",
        sort_direction: str = "desc",
        **filters
    ) -> Dict[str, Any]:
        """Generic resolver for paginated lists"""
        
        # Get database session
        session = await get_db_session().__aenter__()
        
        try:
            # Build base query
            query = await base_query_func(session, **filters)
            
            # Create pagination parameters
            params = PaginationParams(
                first=first,
                after=after,
                last=last,
                before=before,
                sort_field=sort_field,
                sort_direction=SortDirection(sort_direction.lower())
            )
            
            # Create paginator and paginate
            paginator = CursorPaginator(model_class, session)
            result = await paginator.paginate(query, params)
            
            # Log operation
            log_pagination_operation(
                model_name=model_class.__name__,
                page_size=len(result["edges"]),
                total_count=result["total_count"]
            )
            
            return result
            
        finally:
            await session.close()


class AdvancedPaginationMixin:
    """Mixin for advanced pagination features"""
    
    @staticmethod
    async def resolve_paginated_search(
        info,
        model_class,
        search_query: str,
        search_fields: List[str],
        first: Optional[int] = None,
        after: Optional[str] = None,
        **filters
    ) -> Dict[str, Any]:
        """Paginated search with full-text search"""
        
        session = await get_db_session().__aenter__()
        
        try:
            # Build search query
            base_query = session.query(model_class)
            
            # Apply search filters
            if search_query:
                search_conditions = []
                for field in search_fields:
                    column = getattr(model_class, field)
                    search_conditions.append(column.ilike(f"%{search_query}%"))
                
                base_query = base_query.filter(or_(*search_conditions))
            
            # Apply additional filters
            for field, value in filters.items():
                if value is not None and hasattr(model_class, field):
                    column = getattr(model_class, field)
                    base_query = base_query.filter(column == value)
            
            # Paginate
            params = PaginationParams(
                first=first,
                after=after,
                sort_field="relevance",  # Would implement relevance scoring
                sort_direction=SortDirection.DESC
            )
            
            paginator = CursorPaginator(model_class, session)
            result = await paginator.paginate(base_query, params)
            
            return result
            
        finally:
            await session.close()
    
    @staticmethod
    async def resolve_paginated_aggregation(
        info,
        model_class,
        aggregation_field: str,
        aggregation_type: str = "count",
        group_by_field: Optional[str] = None,
        first: Optional[int] = None,
        after: Optional[str] = None
    ) -> Dict[str, Any]:
        """Paginated aggregation results"""
        
        session = await get_db_session().__aenter__()
        
        try:
            # Build aggregation query
            if aggregation_type == "count":
                agg_func = func.count(getattr(model_class, aggregation_field))
            elif aggregation_type == "sum":
                agg_func = func.sum(getattr(model_class, aggregation_field))
            elif aggregation_type == "avg":
                agg_func = func.avg(getattr(model_class, aggregation_field))
            else:
                agg_func = func.count(getattr(model_class, aggregation_field))
            
            if group_by_field:
                group_column = getattr(model_class, group_by_field)
                base_query = session.query(group_column, agg_func.label("value")).group_by(group_column)
            else:
                base_query = session.query(agg_func.label("value"))
            
            # Create a temporary model for aggregation results
            class AggregationResult:
                def __init__(self, group_value, aggregation_value):
                    self.group_value = group_value
                    self.value = aggregation_value
                    self.id = f"{group_value}_{aggregation_value}"  # For cursor
            
            # Execute and convert results
            raw_results = await session.execute(base_query)
            agg_results = []
            for row in raw_results:
                if group_by_field:
                    agg_results.append(AggregationResult(row[0], row[1]))
                else:
                    agg_results.append(AggregationResult("total", row[0]))
            
            # Manual pagination for aggregation results
            start_idx = 0
            if after:
                # Find start index based on cursor
                cursor_info = CursorInfo.decode(after)
                for i, result in enumerate(agg_results):
                    if result.id == cursor_info.value:
                        start_idx = i + 1
                        break
            
            page_size = first or 20
            end_idx = start_idx + page_size
            page_results = agg_results[start_idx:end_idx]
            
            # Create edges
            edges = []
            for result in page_results:
                cursor_info = CursorInfo(
                    value=result.id,
                    field="id",
                    direction=SortDirection.ASC
                )
                edges.append({
                    "node": result,
                    "cursor": cursor_info.encode()
                })
            
            # Create page info
            page_info = {
                "has_next_page": end_idx < len(agg_results),
                "has_previous_page": start_idx > 0,
                "start_cursor": edges[0]["cursor"] if edges else None,
                "end_cursor": edges[-1]["cursor"] if edges else None
            }
            
            return {
                "edges": edges,
                "page_info": page_info,
                "total_count": len(agg_results)
            }
            
        finally:
            await session.close()


class {{EntityName}}PaginatedQuery(PaginatedQuery, AdvancedPaginationMixin):
    """Paginated queries for {{entity_description}}"""
    
    # Standard paginated list
    {{entity_name}}_connection = ConnectionField(
        {{EntityName}}Connection,
        sort_field=String(default_value="created_at"),
        sort_direction=String(default_value="desc"),
        status=String(),
        category=String(),
        user_id=String(),
        description="Paginated list of {{entity_description}}"
    )
    
    # Paginated search
    search_{{entity_name}}_connection = ConnectionField(
        {{EntityName}}Connection,
        query=String(required=True),
        category=String(),
        description="Paginated search results for {{entity_description}}"
    )
    
    # Paginated user's entities
    my_{{entity_name}}_connection = ConnectionField(
        {{EntityName}}Connection,
        status=String(),
        description="Paginated list of user's {{entity_description}}"
    )
    
    @log_pagination_operation
    async def resolve_{{entity_name}}_connection(
        self, 
        info, 
        first=None, 
        after=None, 
        last=None, 
        before=None,
        sort_field="created_at",
        sort_direction="desc",
        **filters
    ):
        """Resolve paginated {{entity_description}} list"""
        
        async def build_base_query(session, **filters):
            query = session.query({{EntityName}}Model)
            
            # Apply filters
            if filters.get("status"):
                query = query.filter({{EntityName}}Model.status == filters["status"])
            if filters.get("category"):
                query = query.filter({{EntityName}}Model.category == filters["category"])
            if filters.get("user_id"):
                query = query.filter({{EntityName}}Model.created_by_id == filters["user_id"])
            
            # Apply user permissions
            user = await get_current_user(info.context["request"])
            if user:
                # Users can see their own + public entities
                query = query.filter(
                    or_(
                        {{EntityName}}Model.created_by_id == user.id,
                        {{EntityName}}Model.visibility == "public"
                    )
                )
            else:
                # Anonymous users only see public entities
                query = query.filter({{EntityName}}Model.visibility == "public")
            
            return query
        
        return await self.resolve_paginated_list(
            info=info,
            model_class={{EntityName}}Model,
            base_query_func=build_base_query,
            first=first,
            after=after,
            last=last,
            before=before,
            sort_field=sort_field,
            sort_direction=sort_direction,
            **filters
        )
    
    @log_pagination_operation
    async def resolve_search_{{entity_name}}_connection(
        self,
        info,
        query,
        first=None,
        after=None,
        **filters
    ):
        """Resolve paginated search results"""
        
        search_fields = ["name", "description", "tags"]
        
        return await self.resolve_paginated_search(
            info=info,
            model_class={{EntityName}}Model,
            search_query=query,
            search_fields=search_fields,
            first=first,
            after=after,
            **filters
        )
    
    @log_pagination_operation
    async def resolve_my_{{entity_name}}_connection(
        self,
        info,
        first=None,
        after=None,
        **filters
    ):
        """Resolve user's paginated {{entity_description}} list"""
        
        user = await get_current_user(info.context["request"])
        if not user:
            raise PaginationException("Authentication required")
        
        # Add user filter
        filters["user_id"] = user.id
        
        return await self.resolve_{{entity_name}}_connection(
            info=info,
            first=first,
            after=after,
            **filters
        )


# Helper functions for template usage
def create_connection_field(
    connection_class: type,
    description: str,
    additional_args: Optional[Dict[str, Any]] = None
) -> ConnectionField:
    """Create a connection field with standard pagination arguments"""
    
    args = {
        "sort_field": String(default_value="created_at"),
        "sort_direction": String(default_value="desc")
    }
    
    if additional_args:
        args.update(additional_args)
    
    return ConnectionField(connection_class, description=description, **args)


def encode_cursor(value: Any, field: str = "id") -> str:
    """Encode a cursor for pagination"""
    cursor_info = CursorInfo(value=value, field=field)
    return cursor_info.encode()


def decode_cursor(cursor: str) -> CursorInfo:
    """Decode a pagination cursor"""
    return CursorInfo.decode(cursor)


# Export for template system
__all__ = [
    "{{EntityName}}Connection",
    "{{EntityName}}Edge", 
    "{{EntityName}}PageInfo",
    "{{EntityName}}PaginatedQuery",
    "CursorPaginator",
    "PaginationParams",
    "CursorInfo",
    "PaginatedQuery",
    "AdvancedPaginationMixin",
    "PaginationDirection",
    "SortDirection",
    "create_connection_field",
    "encode_cursor",
    "decode_cursor"
]