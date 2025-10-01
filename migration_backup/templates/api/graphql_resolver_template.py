"""GraphQL Resolver Template for IA Chéries Platform
Enterprise-grade GraphQL resolvers with advanced caching and optimization

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
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

import graphene
from graphene import Context
from graphql import GraphQLResolveInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, text

from core.config import get_settings
from core.database import get_db_session
from core.auth import get_current_user, verify_permissions
from core.caching import cache_resolver, invalidate_cache_pattern
from core.rate_limiting import resolver_rate_limit
from core.validation import validate_resolver_args
from core.logging import log_resolver_execution
from utils.exceptions import ResolverException, AuthenticationException
from utils.pagination import apply_cursor_pagination
from utils.filtering import apply_graphql_filters
from utils.sorting import apply_graphql_sorting
from monitoring.api_metrics import GraphQLResolverMetrics

logger = logging.getLogger(__name__)
settings = get_settings()


class ResolverContext:
    """Enhanced context for GraphQL resolvers"""
    
    def __init__(self, info: GraphQLResolveInfo):
        self.info = info
        self.request = info.context.get("request")
        self.user = None
        self.session = None
        self.cache = {}
        self.loader_cache = {}
        self.metrics = GraphQLResolverMetrics()
    
    async def get_user(self):
        """Get authenticated user with caching"""
        if self.user is None and self.request:
            self.user = await get_current_user(self.request)
        return self.user
    
    async def get_session(self):
        """Get database session"""
        if self.session is None:
            self.session = await get_db_session().__aenter__()
        return self.session
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()


class DataLoader:
    """Advanced DataLoader for N+1 query optimization"""
    
    def __init__(self, batch_load_fn: Callable, max_batch_size: int = 100, cache: bool = True):
        self.batch_load_fn = batch_load_fn
        self.max_batch_size = max_batch_size
        self.cache_enabled = cache
        self._cache = {}
        self._queue = []
        self._future_cache = {}
        self._scheduled = False
    
    async def load(self, key: Any) -> Any:
        """Load single item with batching"""
        if self.cache_enabled and key in self._cache:
            return self._cache[key]
        
        if key in self._future_cache:
            return await self._future_cache[key]
        
        future = asyncio.Future()
        self._future_cache[key] = future
        self._queue.append(key)
        
        if not self._scheduled:
            self._scheduled = True
            asyncio.create_task(self._dispatch())
        
        return await future
    
    async def load_many(self, keys: List[Any]) -> List[Any]:
        """Load multiple items with batching"""
        return await asyncio.gather(*[self.load(key) for key in keys])
    
    async def _dispatch(self):
        """Dispatch batched requests"""
        await asyncio.sleep(0)  # Allow more items to accumulate
        
        if not self._queue:
            self._scheduled = False
            return
        
        # Process in batches
        while self._queue:
            batch_keys = self._queue[:self.max_batch_size]
            self._queue = self._queue[self.max_batch_size:]
            
            try:
                results = await self.batch_load_fn(batch_keys)
                result_map = dict(zip(batch_keys, results))
                
                for key in batch_keys:
                    result = result_map.get(key)
                    if self.cache_enabled:
                        self._cache[key] = result
                    
                    if key in self._future_cache:
                        future = self._future_cache.pop(key)
                        if not future.done():
                            future.set_result(result)
            
            except Exception as e:
                for key in batch_keys:
                    if key in self._future_cache:
                        future = self._future_cache.pop(key)
                        if not future.done():
                            future.set_exception(e)
        
        self._scheduled = False
    
    def clear_cache(self):
        """Clear loader cache"""
        self._cache.clear()


class {{EntityName}}Resolver:
    """Enterprise resolver for {{entity_description}} with advanced optimization"""
    
    def __init__(self):
        self.metrics = GraphQLResolverMetrics()
        self._loaders = {}
    
    def get_loader(self, context: ResolverContext, loader_name: str) -> DataLoader:
        """Get or create DataLoader instance"""
        cache_key = f"{loader_name}_{id(context)}"
        
        if cache_key not in self._loaders:
            if loader_name == "{{entity_name}}_by_id":
                self._loaders[cache_key] = DataLoader(self._batch_load_by_ids)
            elif loader_name == "{{entity_name}}_relations":
                self._loaders[cache_key] = DataLoader(self._batch_load_relations)
            elif loader_name == "{{entity_name}}_analytics":
                self._loaders[cache_key] = DataLoader(self._batch_load_analytics)
            else:
                raise ValueError(f"Unknown loader: {loader_name}")
        
        return self._loaders[cache_key]
    
    async def _batch_load_by_ids(self, ids: List[str]) -> List[Any]:
        """Batch load entities by IDs"""
        async with get_db_session() as session:
            query = (
                session.query({{EntityName}}Model)
                .filter({{EntityName}}Model.id.in_(ids))
                .options(
                    selectinload({{EntityName}}Model.creator),
                    selectinload({{EntityName}}Model.categories),
                    joinedload({{EntityName}}Model.metadata)
                )
            )
            
            entities = await session.execute(query)
            entity_map = {str(entity.id): entity for entity in entities.scalars()}
            
            # Return in same order as requested IDs
            return [entity_map.get(str(id)) for id in ids]
    
    async def _batch_load_relations(self, entity_ids: List[str]) -> List[List[Any]]:
        """Batch load related entities"""
        async with get_db_session() as session:
            # Load all relations in one query
            query = (
                session.query({{EntityName}}RelationModel)
                .filter({{EntityName}}RelationModel.{{entity_name}}_id.in_(entity_ids))
                .options(selectinload({{EntityName}}RelationModel.related_entity))
            )
            
            relations = await session.execute(query)
            relations_map = {}
            
            for relation in relations.scalars():
                entity_id = str(relation.{{entity_name}}_id)
                if entity_id not in relations_map:
                    relations_map[entity_id] = []
                relations_map[entity_id].append(relation.related_entity)
            
            return [relations_map.get(str(id), []) for id in entity_ids]
    
    async def _batch_load_analytics(self, entity_ids: List[str]) -> List[Dict[str, Any]]:
        """Batch load analytics data"""
        async with get_db_session() as session:
            # Aggregate analytics query
            query = text("""
                SELECT 
                    entity_id,
                    COUNT(*) as view_count,
                    SUM(engagement_score) as total_engagement,
                    AVG(rating) as avg_rating,
                    COUNT(DISTINCT user_id) as unique_users
                FROM analytics_events 
                WHERE entity_id = ANY(:entity_ids)
                AND created_at >= NOW() - INTERVAL '30 days'
                GROUP BY entity_id
            """)
            
            result = await session.execute(query, {"entity_ids": entity_ids})
            analytics_map = {
                str(row.entity_id): {
                    "view_count": row.view_count,
                    "total_engagement": float(row.total_engagement or 0),
                    "avg_rating": float(row.avg_rating or 0),
                    "unique_users": row.unique_users
                }
                for row in result
            }
            
            # Return default analytics for entities without data
            default_analytics = {
                "view_count": 0,
                "total_engagement": 0.0,
                "avg_rating": 0.0,
                "unique_users": 0
            }
            
            return [analytics_map.get(str(id), default_analytics) for id in entity_ids]
    
    @log_resolver_execution
    @cache_resolver(ttl=300, key_prefix="{{entity_name}}_resolver")
    @resolver_rate_limit(calls=100, period=60)
    async def resolve_{{entity_name}}(self, info: GraphQLResolveInfo, id: str) -> Optional[Any]:
        """Resolve single {{entity_description}} with caching and optimization"""
        context = ResolverContext(info)
        
        try:
            # Load using DataLoader for N+1 optimization
            loader = self.get_loader(context, "{{entity_name}}_by_id")
            entity = await loader.load(id)
            
            if not entity:
                return None
            
            # Check permissions
            user = await context.get_user()
            if not await self._can_access_entity(entity, user):
                raise AuthenticationException("Insufficient permissions")
            
            # Record metrics
            self.metrics.record_resolution("{{entity_name}}", "single", user.id if user else None)
            
            return entity
            
        except Exception as e:
            logger.error(f"Error resolving {{entity_description}} {id}: {str(e)}")
            raise ResolverException(f"Failed to resolve {{entity_description}}")
        
        finally:
            await context.cleanup()
    
    @log_resolver_execution
    @cache_resolver(ttl=600, key_prefix="{{entity_name}}_list_resolver")
    async def resolve_{{entity_name}}_list(
        self, 
        info: GraphQLResolveInfo, 
        filter: Optional[Dict] = None,
        sort: Optional[Dict] = None,
        first: Optional[int] = None,
        after: Optional[str] = None
    ) -> Dict[str, Any]:
        """Resolve paginated list with advanced filtering and sorting"""
        context = ResolverContext(info)
        
        try:
            session = await context.get_session()
            user = await context.get_user()
            
            # Build base query with permissions
            query = session.query({{EntityName}}Model)
            query = await self._apply_user_permissions(query, user)
            
            # Apply filters
            if filter:
                query = apply_graphql_filters(query, filter, {{EntityName}}Model)
            
            # Apply sorting
            if sort:
                query = apply_graphql_sorting(query, sort, {{EntityName}}Model)
            else:
                query = query.order_by({{EntityName}}Model.created_at.desc())
            
            # Optimize with eager loading
            query = query.options(
                selectinload({{EntityName}}Model.creator),
                selectinload({{EntityName}}Model.categories),
                joinedload({{EntityName}}Model.metadata)
            )
            
            # Apply pagination
            result = await apply_cursor_pagination(
                query=query,
                first=first or 20,
                after=after,
                cursor_field={{EntityName}}Model.id
            )
            
            # Prefetch related data using DataLoader
            if result["edges"]:
                entity_ids = [edge["node"].id for edge in result["edges"]]
                
                # Prefetch relations and analytics in parallel
                relations_loader = self.get_loader(context, "{{entity_name}}_relations")
                analytics_loader = self.get_loader(context, "{{entity_name}}_analytics")
                
                await asyncio.gather(
                    relations_loader.load_many(entity_ids),
                    analytics_loader.load_many(entity_ids)
                )
            
            # Record metrics
            self.metrics.record_resolution(
                "{{entity_name}}", 
                "list", 
                user.id if user else None,
                metadata={"count": len(result["edges"])}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error resolving {{entity_description}} list: {str(e)}")
            raise ResolverException("Failed to resolve {{entity_description}} list")
        
        finally:
            await context.cleanup()
    
    @log_resolver_execution
    async def resolve_{{entity_name}}_search(
        self, 
        info: GraphQLResolveInfo, 
        query: str,
        filter: Optional[Dict] = None,
        first: Optional[int] = None,
        after: Optional[str] = None
    ) -> Dict[str, Any]:
        """Resolve full-text search with relevance scoring"""
        context = ResolverContext(info)
        
        try:
            session = await context.get_session()
            user = await context.get_user()
            
            # Build search query with PostgreSQL full-text search
            search_query = session.query({{EntityName}}Model)
            
            # Apply full-text search
            search_vector = func.to_tsvector('english', 
                func.coalesce({{EntityName}}Model.name, '') + ' ' +
                func.coalesce({{EntityName}}Model.description, '') + ' ' +
                func.coalesce({{EntityName}}Model.tags, '')
            )
            search_tsquery = func.plainto_tsquery('english', query)
            
            search_query = search_query.filter(search_vector.match(search_tsquery))
            
            # Add relevance ranking
            rank = func.ts_rank(search_vector, search_tsquery)
            search_query = search_query.add_columns(rank.label('rank'))
            search_query = search_query.order_by(rank.desc())
            
            # Apply user permissions and filters
            search_query = await self._apply_user_permissions(search_query, user)
            if filter:
                search_query = apply_graphql_filters(search_query, filter, {{EntityName}}Model)
            
            # Optimize with eager loading
            search_query = search_query.options(
                selectinload({{EntityName}}Model.creator),
                selectinload({{EntityName}}Model.categories)
            )
            
            # Apply pagination
            result = await apply_cursor_pagination(
                query=search_query,
                first=first or 20,
                after=after,
                cursor_field={{EntityName}}Model.id
            )
            
            # Record metrics
            self.metrics.record_search("{{entity_name}}", query, user.id if user else None)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in {{entity_description}} search: {str(e)}")
            raise ResolverException("Search failed")
        
        finally:
            await context.cleanup()
    
    @log_resolver_execution
    @cache_resolver(ttl=3600, key_prefix="{{entity_name}}_analytics")
    async def resolve_{{entity_name}}_analytics(
        self, 
        info: GraphQLResolveInfo,
        entity_id: Optional[str] = None,
        date_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """Resolve analytics data with aggregation"""
        context = ResolverContext(info)
        
        try:
            user = await context.get_user()
            if not user:
                raise AuthenticationException("Authentication required")
            
            # Determine date range
            if date_range == "7d":
                start_date = datetime.utcnow() - timedelta(days=7)
            elif date_range == "30d":
                start_date = datetime.utcnow() - timedelta(days=30)
            elif date_range == "90d":
                start_date = datetime.utcnow() - timedelta(days=90)
            else:
                start_date = datetime.utcnow() - timedelta(days=30)  # Default
            
            session = await context.get_session()
            
            # Base analytics query
            analytics_query = text("""
                WITH daily_stats AS (
                    SELECT 
                        DATE_TRUNC('day', created_at) as date,
                        entity_id,
                        COUNT(*) as daily_views,
                        SUM(engagement_score) as daily_engagement,
                        COUNT(DISTINCT user_id) as daily_unique_users
                    FROM analytics_events 
                    WHERE created_at >= :start_date
                    AND (:entity_id IS NULL OR entity_id = :entity_id)
                    GROUP BY DATE_TRUNC('day', created_at), entity_id
                ),
                aggregated_stats AS (
                    SELECT 
                        entity_id,
                        SUM(daily_views) as total_views,
                        SUM(daily_engagement) as total_engagement,
                        MAX(daily_unique_users) as peak_users,
                        AVG(daily_views) as avg_daily_views,
                        COUNT(*) as active_days
                    FROM daily_stats
                    GROUP BY entity_id
                )
                SELECT 
                    COALESCE(entity_id::text, 'all') as entity_id,
                    total_views,
                    total_engagement,
                    peak_users,
                    avg_daily_views,
                    active_days,
                    array_agg(
                        json_build_object(
                            'date', ds.date,
                            'views', ds.daily_views,
                            'engagement', ds.daily_engagement,
                            'unique_users', ds.daily_unique_users
                        ) ORDER BY ds.date
                    ) as daily_breakdown
                FROM aggregated_stats agg
                LEFT JOIN daily_stats ds ON agg.entity_id = ds.entity_id
                GROUP BY entity_id, total_views, total_engagement, peak_users, avg_daily_views, active_days
            """)
            
            result = await session.execute(analytics_query, {
                "start_date": start_date,
                "entity_id": entity_id
            })
            
            analytics_data = {}
            for row in result:
                analytics_data[row.entity_id] = {
                    "total_views": int(row.total_views or 0),
                    "total_engagement": float(row.total_engagement or 0),
                    "peak_users": int(row.peak_users or 0),
                    "avg_daily_views": float(row.avg_daily_views or 0),
                    "active_days": int(row.active_days or 0),
                    "daily_breakdown": row.daily_breakdown or []
                }
            
            # Record metrics
            self.metrics.record_analytics_query(entity_id, date_range, user.id)
            
            return analytics_data.get(entity_id or "all", {})
            
        except Exception as e:
            logger.error(f"Error resolving analytics: {str(e)}")
            raise ResolverException("Analytics resolution failed")
        
        finally:
            await context.cleanup()
    
    async def _can_access_entity(self, entity: Any, user: Optional[Any]) -> bool:
        """Check if user can access entity"""
        if not entity:
            return False
        
        # Public entities
        if entity.visibility == "public":
            return True
        
        # Require authentication for non-public entities
        if not user:
            return False
        
        # Owner access
        if entity.created_by_id == user.id:
            return True
        
        # Admin access
        if await verify_permissions(user, "admin_{{entity_name}}"):
            return True
        
        # Collaborative access
        if entity.visibility == "collaborative":
            return await self._has_collaborative_access(entity, user)
        
        return False
    
    async def _has_collaborative_access(self, entity: Any, user: Any) -> bool:
        """Check collaborative access permissions"""
        async with get_db_session() as session:
            collaboration = await session.query({{EntityName}}CollaborationModel).filter(
                and_(
                    {{EntityName}}CollaborationModel.{{entity_name}}_id == entity.id,
                    {{EntityName}}CollaborationModel.user_id == user.id,
                    {{EntityName}}CollaborationModel.status == "active"
                )
            ).first()
            
            return collaboration is not None
    
    async def _apply_user_permissions(self, query, user: Optional[Any]):
        """Apply user-based query permissions"""
        if not user:
            # Anonymous users only see public content
            return query.filter({{EntityName}}Model.visibility == "public")
        
        if await verify_permissions(user, "admin_{{entity_name}}"):
            # Admins see everything
            return query
        
        # Regular users see public + own + collaborative content
        return query.filter(
            or_(
                {{EntityName}}Model.visibility == "public",
                {{EntityName}}Model.created_by_id == user.id,
                and_(
                    {{EntityName}}Model.visibility == "collaborative",
                    {{EntityName}}Model.id.in_(
                        session.query({{EntityName}}CollaborationModel.{{entity_name}}_id)
                        .filter(
                            {{EntityName}}CollaborationModel.user_id == user.id,
                            {{EntityName}}CollaborationModel.status == "active"
                        )
                    )
                )
            )
        )


# Create global resolver instance
{{entity_name}}_resolver = {{EntityName}}Resolver()


# Export resolver functions for GraphQL schema
async def resolve_{{entity_name}}(root, info, id):
    """GraphQL field resolver for single {{entity_description}}"""
    return await {{entity_name}}_resolver.resolve_{{entity_name}}(info, id)


async def resolve_{{entity_name}}_list(root, info, **kwargs):
    """GraphQL field resolver for {{entity_description}} list"""
    return await {{entity_name}}_resolver.resolve_{{entity_name}}_list(info, **kwargs)


async def resolve_{{entity_name}}_search(root, info, **kwargs):
    """GraphQL field resolver for {{entity_description}} search"""
    return await {{entity_name}}_resolver.resolve_{{entity_name}}_search(info, **kwargs)


async def resolve_{{entity_name}}_analytics(root, info, **kwargs):
    """GraphQL field resolver for {{entity_description}} analytics"""
    return await {{entity_name}}_resolver.resolve_{{entity_name}}_analytics(info, **kwargs)


# Export for template system
__all__ = [
    "{{EntityName}}Resolver",
    "ResolverContext",
    "DataLoader",
    "resolve_{{entity_name}}",
    "resolve_{{entity_name}}_list", 
    "resolve_{{entity_name}}_search",
    "resolve_{{entity_name}}_analytics"
]