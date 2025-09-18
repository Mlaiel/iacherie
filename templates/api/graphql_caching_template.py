"""
🔒 GRAPHQL CACHING TEMPLATE - ENTERPRISE CACHING IMPLEMENTATION
==============================================================

© 2025 Fahed Mlaiel <mlaiel@live.de)
TOUS DROITS RÉSERVÉS

Enterprise-grade GraphQL caching template with:
- Query result caching
- Field-level caching
- Cache invalidation strategies
- Performance optimization
- Redis integration

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib
import json
from datetime import datetime, timedelta

import strawberry
from strawberry.extensions import Extension
from strawberry.types import Info
import redis.asyncio as redis
from pydantic import BaseModel, Field

from ..template_registry import TemplateInterface, TemplateMetadata, TemplateType, TemplateCategory, SecurityLevel

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategy types."""
    NO_CACHE = "no_cache"
    QUERY_CACHE = "query_cache"
    FIELD_CACHE = "field_cache"
    PERSISTED_QUERY = "persisted_query"
    AUTOMATIC = "automatic"


class GraphQLCachingConfig(BaseModel):
    """Configuration for GraphQL caching generation."""
    
    caching_name: str = Field(..., description="Name of the caching configuration")
    description: str = Field("", description="Caching description")
    
    # Redis configuration
    redis_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "host": "localhost",
            "port": 6379,
            "db": 1,
            "max_connections": 100,
            "key_prefix": "graphql_cache:"
        }
    )
    
    # Cache configuration
    cache_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "default_ttl": 300,
            "max_ttl": 3600,
            "enabled": True,
            "strategy": "automatic",
            "compression": True
        }
    )
    
    # Field-specific caching
    field_cache_rules: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Field-specific cache rules"
    )
    
    # Query caching rules
    query_cache_rules: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Query-specific cache rules"
    )


class GraphQLCachingTemplate(TemplateInterface):
    """Enterprise GraphQL caching template."""
    
    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="graphql_caching_template",
            template_type=TemplateType.GRAPHQL,
            category=TemplateCategory.ADVANCED,
            version="1.0.0",
            author="Fahed Mlaiel",
            description="Enterprise GraphQL caching template with Redis integration",
            security_level=SecurityLevel.ENTERPRISE,
            dependencies=["strawberry-graphql", "redis", "pydantic"],
            tags=["graphql", "caching", "redis", "performance"],
            enterprise_features=[
                "Query result caching",
                "Field-level caching", 
                "Cache invalidation",
                "Performance optimization",
                "Compression support"
            ]
        )
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate GraphQL caching based on configuration."""
        try:
            caching_config = GraphQLCachingConfig(**config)
            return self._generate_caching_code(caching_config)
        except Exception as e:
            logger.error(f"Failed to generate GraphQL caching: {e}")
            raise
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate caching configuration."""
        try:
            GraphQLCachingConfig(**config)
            return True
        except Exception as e:
            logger.error(f"Invalid GraphQL caching config: {e}")
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for configuration."""
        return GraphQLCachingConfig.schema()
    
    def get_examples(self) -> List[Dict[str, Any]]:
        """Return example configurations."""
        return [
            {
                "caching_name": "CreatorCaching",
                "description": "Caching configuration for creator economy GraphQL API",
                "field_cache_rules": {
                    "Creator.content": {
                        "ttl": 600,
                        "strategy": "field_cache",
                        "invalidate_on": ["content_updated", "content_created"]
                    },
                    "Content.analytics": {
                        "ttl": 300,
                        "strategy": "field_cache",
                        "depends_on": ["user_id", "date_range"]
                    }
                },
                "query_cache_rules": {
                    "getCreator": {
                        "ttl": 900,
                        "strategy": "query_cache",
                        "cache_key_fields": ["id"]
                    }
                }
            }
        ]
    
    def _generate_caching_code(self, config: GraphQLCachingConfig) -> str:
        """Generate the actual GraphQL caching code."""
        
        # Generate imports
        imports = self._generate_imports()
        
        # Generate cache manager
        cache_manager = self._generate_cache_manager(config)
        
        # Generate caching extensions
        caching_extensions = self._generate_caching_extensions(config)
        
        # Generate cache decorators
        cache_decorators = self._generate_cache_decorators(config)
        
        # Generate invalidation system
        invalidation_system = self._generate_invalidation_system(config)
        
        # Generate configuration
        caching_config_code = self._generate_caching_config(config)
        
        code = f'''"""
{config.caching_name} GraphQL Caching
Generated by Ainflue GraphQL Caching Template

{config.description}

🔒 PROTECTION INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
"""

{imports}

{cache_manager}

{caching_extensions}

{cache_decorators}

{invalidation_system}

{caching_config_code}

# Caching factory
def create_cache_manager() -> GraphQLCacheManager:
    """Create cache manager with configuration."""
    manager = GraphQLCacheManager()
    
    # Apply cache strategies
    manager = apply_cache_strategies(manager)
    
    # Apply monitoring
    manager = apply_cache_monitoring(manager)
    
    return manager

# Export cache manager
cache_manager = create_cache_manager()

if __name__ == "__main__":
    print(f"✅ {config.caching_name} initialized successfully")
    print(f"📊 Caching statistics:")
    print(f"   - Default TTL: {config.cache_config['default_ttl']}s")
    print(f"   - Field cache rules: {len(config.field_cache_rules)}")
    print(f"   - Query cache rules: {len(config.query_cache_rules)}")
    print(f"   - Compression: {config.cache_config['compression']}")
'''
        
        return code
    
    def _generate_imports(self) -> str:
        """Generate import statements."""
        return '''from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
import logging
import hashlib
import json
import gzip
from functools import wraps
import asyncio

import strawberry
from strawberry.extensions import Extension
from strawberry.types import Info
from strawberry.field import StrawberryField

import redis.asyncio as redis
from pydantic import BaseModel

logger = logging.getLogger(__name__)'''
    
    def _generate_cache_manager(self, config: GraphQLCachingConfig) -> str:
        """Generate cache manager implementation."""
        redis_config = config.redis_config
        cache_config = config.cache_config
        
        return f'''# GraphQL Cache Manager

class GraphQLCacheManager:
    """GraphQL caching manager with Redis backend."""
    
    def __init__(self):
        self.redis_client = None
        self.redis_config = {redis_config}
        self.cache_config = {cache_config}
        self.compression_enabled = {cache_config.get('compression', True)}
        self.key_prefix = self.redis_config['key_prefix']
    
    async def connect(self):
        """Connect to Redis."""
        if self.redis_client is None:
            try:
                self.redis_client = redis.Redis(
                    host=self.redis_config['host'],
                    port=self.redis_config['port'],
                    db=self.redis_config['db'],
                    max_connections=self.redis_config['max_connections'],
                    decode_responses=False  # Handle compression manually
                )
                await self.redis_client.ping()
                logger.info("Connected to Redis for GraphQL caching")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {{e}}")
                raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    def _generate_cache_key(self, key_type: str, *args) -> str:
        """Generate cache key."""
        key_parts = [self.key_prefix, key_type] + [str(arg) for arg in args if arg is not None]
        return ":".join(key_parts)
    
    def _hash_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """Generate hash for query and variables."""
        content = query
        if variables:
            content += json.dumps(variables, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _compress_data(self, data: str) -> bytes:
        """Compress data if compression is enabled."""
        if self.compression_enabled:
            return gzip.compress(data.encode())
        return data.encode()
    
    def _decompress_data(self, data: bytes) -> str:
        """Decompress data if compression is enabled."""
        if self.compression_enabled:
            try:
                return gzip.decompress(data).decode()
            except:
                # Fallback to uncompressed data
                return data.decode()
        return data.decode()
    
    async def get_query_cache(
        self, 
        query: str, 
        variables: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """Get cached query result."""
        if not self.cache_config['enabled']:
            return None
        
        await self.connect()
        
        query_hash = self._hash_query(query, variables)
        cache_key = self._generate_cache_key("query", query_hash)
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                decompressed_data = self._decompress_data(cached_data)
                return json.loads(decompressed_data)
        except Exception as e:
            logger.warning(f"Failed to get query cache: {{e}}")
        
        return None
    
    async def set_query_cache(
        self,
        query: str,
        variables: Optional[Dict[str, Any]],
        result: Any,
        ttl: Optional[int] = None
    ):
        """Set query result in cache."""
        if not self.cache_config['enabled'] or not result:
            return
        
        await self.connect()
        
        query_hash = self._hash_query(query, variables)
        cache_key = self._generate_cache_key("query", query_hash)
        ttl = ttl or self.cache_config['default_ttl']
        
        try:
            serialized_data = json.dumps(result, default=str)
            compressed_data = self._compress_data(serialized_data)
            await self.redis_client.setex(cache_key, ttl, compressed_data)
        except Exception as e:
            logger.warning(f"Failed to set query cache: {{e}}")
    
    async def get_field_cache(
        self,
        field_name: str,
        parent_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """Get cached field result."""
        if not self.cache_config['enabled']:
            return None
        
        await self.connect()
        
        context_hash = ""
        if context:
            context_hash = hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest()[:8]
        
        cache_key = self._generate_cache_key("field", field_name, parent_id, context_hash)
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                decompressed_data = self._decompress_data(cached_data)
                return json.loads(decompressed_data)
        except Exception as e:
            logger.warning(f"Failed to get field cache: {{e}}")
        
        return None
    
    async def set_field_cache(
        self,
        field_name: str,
        parent_id: str,
        result: Any,
        context: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ):
        """Set field result in cache."""
        if not self.cache_config['enabled'] or result is None:
            return
        
        await self.connect()
        
        context_hash = ""
        if context:
            context_hash = hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest()[:8]
        
        cache_key = self._generate_cache_key("field", field_name, parent_id, context_hash)
        ttl = ttl or self.cache_config['default_ttl']
        
        try:
            serialized_data = json.dumps(result, default=str)
            compressed_data = self._compress_data(serialized_data)
            await self.redis_client.setex(cache_key, ttl, compressed_data)
        except Exception as e:
            logger.warning(f"Failed to set field cache: {{e}}")
    
    async def invalidate_cache(self, pattern: str):
        """Invalidate cache by pattern."""
        if not self.cache_config['enabled']:
            return
        
        await self.connect()
        
        try:
            full_pattern = self._generate_cache_key(pattern) + "*"
            keys = await self.redis_client.keys(full_pattern)
            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"Invalidated {{len(keys)}} cache entries matching {{pattern}}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {{e}}")'''
    
    def _generate_caching_extensions(self, config: GraphQLCachingConfig) -> str:
        """Generate caching extensions."""
        return '''# GraphQL Caching Extensions

class QueryCacheExtension(Extension):
    """Extension for query-level caching."""
    
    def __init__(self, cache_manager: GraphQLCacheManager):
        self.cache_manager = cache_manager
    
    async def on_request_start(self):
        """Check cache before request execution."""
        query = str(self.execution_context.query)
        variables = self.execution_context.variable_values
        
        # Try to get cached result
        cached_result = await self.cache_manager.get_query_cache(query, variables)
        
        if cached_result:
            # Return cached result
            self.execution_context.result = cached_result
            logger.debug("Returning cached query result")
    
    async def on_request_end(self):
        """Cache result after successful execution."""
        if not self.execution_context.errors and self.execution_context.result:
            query = str(self.execution_context.query)
            variables = self.execution_context.variable_values
            result = self.execution_context.result
            
            # Cache the result
            await self.cache_manager.set_query_cache(query, variables, result)
            logger.debug("Cached query result")

class FieldCacheExtension(Extension):
    """Extension for field-level caching."""
    
    def __init__(self, cache_manager: GraphQLCacheManager):
        self.cache_manager = cache_manager
        self.field_cache_rules = {}
    
    def add_field_cache_rule(self, field_name: str, ttl: int, context_fields: List[str] = None):
        """Add field cache rule."""
        self.field_cache_rules[field_name] = {
            "ttl": ttl,
            "context_fields": context_fields or []
        }
    
    async def on_field_execution_start(self, field_name: str, field_args: Dict[str, Any], parent_value: Any):
        """Check field cache before execution."""
        if field_name not in self.field_cache_rules:
            return
        
        rule = self.field_cache_rules[field_name]
        parent_id = getattr(parent_value, 'id', None) if parent_value else None
        
        if parent_id:
            # Build context from specified fields
            context = {}
            for context_field in rule['context_fields']:
                if context_field in field_args:
                    context[context_field] = field_args[context_field]
            
            # Try to get cached result
            cached_result = await self.cache_manager.get_field_cache(
                field_name, str(parent_id), context
            )
            
            if cached_result is not None:
                return cached_result
    
    async def on_field_execution_end(
        self, 
        field_name: str, 
        field_args: Dict[str, Any], 
        parent_value: Any, 
        result: Any
    ):
        """Cache field result after execution."""
        if field_name not in self.field_cache_rules or result is None:
            return
        
        rule = self.field_cache_rules[field_name]
        parent_id = getattr(parent_value, 'id', None) if parent_value else None
        
        if parent_id:
            # Build context from specified fields
            context = {}
            for context_field in rule['context_fields']:
                if context_field in field_args:
                    context[context_field] = field_args[context_field]
            
            # Cache the result
            await self.cache_manager.set_field_cache(
                field_name, str(parent_id), result, context, rule['ttl']
            )'''
    
    def _generate_cache_decorators(self, config: GraphQLCachingConfig) -> str:
        """Generate cache decorators."""
        return '''# Cache Decorators

def cache_query(ttl: int = 300, key_fields: List[str] = None):
    """Decorator for caching query results."""
    def decorator(resolver_func: Callable) -> Callable:
        @wraps(resolver_func)
        async def wrapper(*args, **kwargs):
            # Extract cache key from specified fields
            cache_key_parts = []
            if key_fields:
                for field in key_fields:
                    if field in kwargs:
                        cache_key_parts.append(str(kwargs[field]))
            
            cache_key = f"query:{resolver_func.__name__}:" + ":".join(cache_key_parts)
            
            # Try to get from cache
            cached_result = await cache_manager.get_query_cache(cache_key, None)
            if cached_result is not None:
                return cached_result
            
            # Execute resolver
            result = await resolver_func(*args, **kwargs)
            
            # Cache result
            if result is not None:
                await cache_manager.set_query_cache(cache_key, None, result, ttl)
            
            return result
        
        return wrapper
    return decorator

def cache_field(ttl: int = 300, context_fields: List[str] = None):
    """Decorator for caching field results.""" 
    def decorator(resolver_func: Callable) -> Callable:
        @wraps(resolver_func)
        async def wrapper(self, info: Info, *args, **kwargs):
            field_name = info.field_name
            parent = info.parent_value
            parent_id = getattr(parent, 'id', None) if parent else None
            
            if parent_id:
                # Build context from specified fields
                context = {}
                if context_fields:
                    for field in context_fields:
                        if field in kwargs:
                            context[field] = kwargs[field]
                
                # Try to get from cache
                cached_result = await cache_manager.get_field_cache(
                    field_name, str(parent_id), context
                )
                if cached_result is not None:
                    return cached_result
            
            # Execute resolver
            result = await resolver_func(self, info, *args, **kwargs)
            
            # Cache result
            if parent_id and result is not None:
                context = {}
                if context_fields:
                    for field in context_fields:
                        if field in kwargs:
                            context[field] = kwargs[field]
                
                await cache_manager.set_field_cache(
                    field_name, str(parent_id), result, context, ttl
                )
            
            return result
        
        return wrapper
    return decorator

def cache_invalidate(patterns: List[str]):
    """Decorator to invalidate cache after mutation."""
    def decorator(resolver_func: Callable) -> Callable:
        @wraps(resolver_func)
        async def wrapper(*args, **kwargs):
            # Execute mutation
            result = await resolver_func(*args, **kwargs)
            
            # Invalidate cache patterns
            for pattern in patterns:
                await cache_manager.invalidate_cache(pattern)
            
            return result
        
        return wrapper
    return decorator'''
    
    def _generate_invalidation_system(self, config: GraphQLCachingConfig) -> str:
        """Generate cache invalidation system."""
        return '''# Cache Invalidation System

class CacheInvalidationManager:
    """Manager for cache invalidation strategies."""
    
    def __init__(self, cache_manager: GraphQLCacheManager):
        self.cache_manager = cache_manager
        self.invalidation_rules = {}
    
    def add_invalidation_rule(self, event: str, patterns: List[str]):
        """Add cache invalidation rule for event."""
        if event not in self.invalidation_rules:
            self.invalidation_rules[event] = []
        self.invalidation_rules[event].extend(patterns)
    
    async def handle_event(self, event: str, data: Dict[str, Any] = None):
        """Handle cache invalidation event."""
        if event not in self.invalidation_rules:
            return
        
        patterns = self.invalidation_rules[event]
        
        for pattern in patterns:
            # Replace placeholders with actual data
            if data:
                formatted_pattern = pattern.format(**data)
            else:
                formatted_pattern = pattern
            
            await self.cache_manager.invalidate_cache(formatted_pattern)
        
        logger.info(f"Invalidated cache for event: {event}")

# Event-based cache invalidation
async def invalidate_creator_cache(creator_id: str):
    """Invalidate creator-related cache."""
    patterns = [
        f"field:Creator:{creator_id}",
        f"field:content:{creator_id}",
        f"query:getCreator:{creator_id}"
    ]
    
    for pattern in patterns:
        await cache_manager.invalidate_cache(pattern)

async def invalidate_content_cache(content_id: str, creator_id: str):
    """Invalidate content-related cache."""
    patterns = [
        f"field:Content:{content_id}",
        f"field:creator_content:{creator_id}",
        f"query:getContent:{content_id}"
    ]
    
    for pattern in patterns:
        await cache_manager.invalidate_cache(pattern)'''
    
    def _generate_caching_config(self, config: GraphQLCachingConfig) -> str:
        """Generate caching configuration."""
        return f'''# Caching Configuration

CACHING_CONFIG = {config.dict()}

def apply_cache_strategies(manager: GraphQLCacheManager) -> GraphQLCacheManager:
    """Apply cache strategies to manager."""
    # Apply field cache rules
    for field_name, rule in CACHING_CONFIG['field_cache_rules'].items():
        # Configure field-specific caching
        pass
    
    # Apply query cache rules  
    for query_name, rule in CACHING_CONFIG['query_cache_rules'].items():
        # Configure query-specific caching
        pass
    
    return manager

def apply_cache_monitoring(manager: GraphQLCacheManager) -> GraphQLCacheManager:
    """Apply cache monitoring."""
    # Add cache hit/miss metrics
    # Add cache performance monitoring
    # Add cache size monitoring
    return manager

def create_caching_extensions(cache_manager: GraphQLCacheManager) -> List[Extension]:
    """Create caching extensions."""
    extensions = []
    
    if CACHING_CONFIG['cache_config']['strategy'] in ['query_cache', 'automatic']:
        extensions.append(QueryCacheExtension(cache_manager))
    
    if CACHING_CONFIG['cache_config']['strategy'] in ['field_cache', 'automatic']:
        field_extension = FieldCacheExtension(cache_manager)
        
        # Add field cache rules
        for field_name, rule in CACHING_CONFIG['field_cache_rules'].items():
            field_extension.add_field_cache_rule(
                field_name,
                rule.get('ttl', CACHING_CONFIG['cache_config']['default_ttl']),
                rule.get('depends_on', [])
            )
        
        extensions.append(field_extension)
    
    return extensions'''


# Register template
from .template_registry import register_template

register_template(
    GraphQLCachingTemplate,
    GraphQLCachingTemplate().metadata
)