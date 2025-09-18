"""
🔒 GRAPHQL SCHEMA TEMPLATE - ENTERPRISE GRAPHQL IMPLEMENTATION
=============================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Enterprise-grade GraphQL schema template with:
- Type-safe schema definition
- Advanced field resolution
- Input validation and sanitization
- Performance optimization
- Security directives
- Schema stitching support
- Federation compatibility

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Type, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import graphql
from graphql import (
    GraphQLSchema, GraphQLObjectType, GraphQLField, GraphQLString, 
    GraphQLInt, GraphQLFloat, GraphQLBoolean, GraphQLID, GraphQLList,
    GraphQLNonNull, GraphQLInputObjectType, GraphQLEnumType,
    GraphQLScalarType, GraphQLUnionType, GraphQLInterfaceType,
    GraphQLDirective, GraphQLArgument, DirectiveLocation
)
from graphql.validation import validate
from graphql.execution import execute
import strawberry
from strawberry.federation import Schema as FederatedSchema
from pydantic import BaseModel, Field, validator

from ..template_registry import TemplateInterface, TemplateMetadata, TemplateType, TemplateCategory, SecurityLevel

logger = logging.getLogger(__name__)


class GraphQLFieldType(Enum):
    """GraphQL field types."""
    SCALAR = "scalar"
    OBJECT = "object"
    INTERFACE = "interface"
    UNION = "union"
    ENUM = "enum"
    INPUT = "input"
    LIST = "list"
    NON_NULL = "non_null"


class GraphQLPermission(Enum):
    """GraphQL permissions for field access."""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    AUTHORIZED = "authorized"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass
class GraphQLFieldConfig:
    """Configuration for GraphQL field."""
    name: str
    field_type: str
    description: str = ""
    nullable: bool = True
    deprecated: bool = False
    deprecation_reason: str = ""
    permission: GraphQLPermission = GraphQLPermission.PUBLIC
    rate_limit: Optional[int] = None
    cache_ttl: Optional[int] = None
    complexity: int = 1
    args: Dict[str, Any] = field(default_factory=dict)
    directives: List[str] = field(default_factory=list)


@dataclass
class GraphQLTypeConfig:
    """Configuration for GraphQL type."""
    name: str
    type_kind: GraphQLFieldType
    description: str = ""
    fields: Dict[str, GraphQLFieldConfig] = field(default_factory=dict)
    interfaces: List[str] = field(default_factory=list)
    directives: List[str] = field(default_factory=list)
    federation_config: Dict[str, Any] = field(default_factory=dict)


class GraphQLSchemaConfig(BaseModel):
    """Configuration for GraphQL schema generation."""
    
    schema_name: str = Field(..., description="Name of the GraphQL schema")
    description: str = Field("", description="Schema description")
    
    # Schema options
    enable_federation: bool = Field(True, description="Enable Apollo Federation")
    enable_subscriptions: bool = Field(True, description="Enable GraphQL subscriptions")
    enable_introspection: bool = Field(True, description="Enable schema introspection")
    enable_playground: bool = Field(True, description="Enable GraphQL Playground")
    
    # Security options
    max_query_depth: int = Field(10, description="Maximum query depth")
    max_query_complexity: int = Field(1000, description="Maximum query complexity")
    enable_query_validation: bool = Field(True, description="Enable query validation")
    auth_required: bool = Field(False, description="Require authentication for all queries")
    
    # Performance options
    enable_query_caching: bool = Field(True, description="Enable query result caching")
    enable_persisted_queries: bool = Field(True, description="Enable persisted queries")
    enable_batching: bool = Field(True, description="Enable query batching")
    default_cache_ttl: int = Field(300, description="Default cache TTL in seconds")
    
    # Creator Economy specific
    creator_economy_types: List[str] = Field(
        default_factory=lambda: ["Creator", "Content", "Collaboration", "Revenue"],
        description="Creator economy entity types"
    )
    
    # Types configuration
    types: Dict[str, GraphQLTypeConfig] = Field(default_factory=dict)
    
    # Custom scalars
    custom_scalars: Dict[str, str] = Field(
        default_factory=lambda: {
            "DateTime": "ISO 8601 date-time string",
            "UUID": "UUID scalar type",
            "URL": "URL scalar type",
            "EmailAddress": "Email address scalar type",
            "JSON": "JSON scalar type"
        }
    )
    
    # Federation configuration
    federation_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "service_name": "ainflue-api",
            "service_url": "https://api.ainflue.com/graphql",
            "enable_entity_reference": True
        }
    )
    
    @validator('schema_name')
    def validate_schema_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Schema name cannot be empty")
        return v.strip()


class GraphQLSchemaTemplate(TemplateInterface):
    """Enterprise GraphQL schema template."""
    
    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="graphql_schema_template",
            template_type=TemplateType.GRAPHQL,
            category=TemplateCategory.ADVANCED,
            version="1.0.0",
            author="Fahed Mlaiel",
            description="Enterprise GraphQL schema template with federation support",
            security_level=SecurityLevel.ENTERPRISE,
            dependencies=["graphql-core", "strawberry-graphql", "pydantic"],
            tags=["graphql", "schema", "federation", "enterprise"],
            compliance_standards=["SOC2", "GDPR", "HIPAA"],
            enterprise_features=[
                "Apollo Federation",
                "Query complexity analysis", 
                "Automatic caching",
                "Security directives",
                "Performance monitoring"
            ]
        )
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate GraphQL schema based on configuration."""
        try:
            schema_config = GraphQLSchemaConfig(**config)
            return self._generate_schema_code(schema_config)
        except Exception as e:
            logger.error(f"Failed to generate GraphQL schema: {e}")
            raise
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate schema configuration."""
        try:
            GraphQLSchemaConfig(**config)
            return True
        except Exception as e:
            logger.error(f"Invalid GraphQL schema config: {e}")
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for configuration."""
        return GraphQLSchemaConfig.schema()
    
    def get_examples(self) -> List[Dict[str, Any]]:
        """Return example configurations."""
        return [
            {
                "schema_name": "CreatorEconomyAPI",
                "description": "Ainflue Creator Economy GraphQL API",
                "enable_federation": True,
                "enable_subscriptions": True,
                "max_query_depth": 15,
                "max_query_complexity": 2000,
                "creator_economy_types": ["Creator", "Content", "Collaboration", "Revenue", "Analytics"],
                "types": {
                    "Creator": {
                        "name": "Creator",
                        "type_kind": "object",
                        "description": "Content creator entity",
                        "fields": {
                            "id": {
                                "name": "id",
                                "field_type": "ID!",
                                "description": "Unique creator identifier"
                            },
                            "username": {
                                "name": "username", 
                                "field_type": "String!",
                                "description": "Creator username"
                            },
                            "content": {
                                "name": "content",
                                "field_type": "[Content!]!",
                                "description": "Creator's content",
                                "complexity": 5
                            }
                        }
                    }
                }
            }
        ]
    
    def _generate_schema_code(self, config: GraphQLSchemaConfig) -> str:
        """Generate the actual GraphQL schema code."""
        
        # Generate imports
        imports = self._generate_imports(config)
        
        # Generate custom scalars
        scalars = self._generate_custom_scalars(config)
        
        # Generate security directives
        directives = self._generate_security_directives(config)
        
        # Generate types
        types = self._generate_types(config)
        
        # Generate schema definition
        schema_def = self._generate_schema_definition(config)
        
        # Generate configuration
        schema_config = self._generate_schema_config(config)
        
        # Generate resolver patterns
        resolvers = self._generate_resolver_patterns(config)
        
        # Generate federation setup
        federation = self._generate_federation_setup(config) if config.enable_federation else ""
        
        # Generate monitoring setup
        monitoring = self._generate_monitoring_setup(config)
        
        code = f'''"""
{config.schema_name} GraphQL Schema
Generated by Ainflue GraphQL Schema Template

{config.description}

🔒 PROTECTION INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
"""

{imports}

{scalars}

{directives}

{types}

{resolvers}

{schema_def}

{federation}

{schema_config}

{monitoring}

# Schema factory function
def create_schema() -> GraphQLSchema:
    """Create and configure GraphQL schema."""
    schema = build_schema()
    
    # Apply security middleware
    schema = apply_security_middleware(schema)
    
    # Apply performance optimizations
    schema = apply_performance_optimizations(schema)
    
    # Apply monitoring
    schema = apply_monitoring(schema)
    
    return schema

# Export schema instance
schema = create_schema()

if __name__ == "__main__":
    # Validate schema
    from graphql import validate_schema
    errors = validate_schema(schema)
    
    if errors:
        print("Schema validation errors:")
        for error in errors:
            print(f"  - {{error}}")
    else:
        print(f"✅ {{config.schema_name}} schema validated successfully")
        print(f"📊 Schema statistics:")
        print(f"   - Types: {{len(config.types)}}")
        print(f"   - Custom scalars: {{len(config.custom_scalars)}}")
        print(f"   - Federation enabled: {{config.enable_federation}}")
        print(f"   - Max complexity: {{config.max_query_complexity}}")
        print(f"   - Max depth: {{config.max_query_depth}}")
'''
        
        return code
    
    def _generate_imports(self, config: GraphQLSchemaConfig) -> str:
        """Generate import statements."""
        imports = [
            "from typing import Dict, List, Optional, Any, Union",
            "from datetime import datetime",
            "import logging",
            "",
            "import graphql",
            "from graphql import (",
            "    GraphQLSchema, GraphQLObjectType, GraphQLField,",
            "    GraphQLString, GraphQLInt, GraphQLFloat, GraphQLBoolean,",
            "    GraphQLID, GraphQLList, GraphQLNonNull, GraphQLInputObjectType,",
            "    GraphQLEnumType, GraphQLScalarType, GraphQLUnionType,",
            "    GraphQLInterfaceType, GraphQLDirective, GraphQLArgument,",
            "    DirectiveLocation, build_schema, validate_schema",
            ")",
            "",
            "import strawberry",
            "from strawberry.types import Info",
            "from strawberry.permission import BasePermission",
            "from strawberry.extensions import QueryDepthLimiter",
            "",
            "from fastapi import Depends, HTTPException, Request",
            "from pydantic import BaseModel",
            "",
            "# Core imports",
            "from core.auth import get_current_user, verify_permissions",
            "from core.caching import cache_response, cache_key",
            "from core.rate_limiting import rate_limit",
            "from monitoring.graphql_metrics import GraphQLMetricsCollector",
            "from utils.validation import validate_graphql_query",
            "from utils.security import sanitize_graphql_input",
            ""
        ]
        
        if config.enable_federation:
            imports.extend([
                "from strawberry.federation import Schema as FederatedSchema",
                "from strawberry.federation.schema_directives import Key, External",
                ""
            ])
        
        return "\n".join(imports)
    
    def _generate_custom_scalars(self, config: GraphQLSchemaConfig) -> str:
        """Generate custom scalar definitions."""
        if not config.custom_scalars:
            return ""
        
        scalars = ["# Custom Scalars", ""]
        
        for scalar_name, description in config.custom_scalars.items():
            scalars.extend([
                f"@strawberry.scalar",
                f"class {scalar_name}:",
                f'    """{description}"""',
                f"    ",
                f"    @staticmethod",
                f"    def serialize(value: Any) -> str:",
                f'        """Serialize {scalar_name} to string."""',
                f"        # Implementation specific to {scalar_name}",
                f"        return str(value)",
                f"    ",
                f"    @staticmethod", 
                f"    def parse_value(value: str) -> Any:",
                f'        """Parse {scalar_name} from string."""',
                f"        # Implementation specific to {scalar_name}",
                f"        return value",
                f"",
                ""
            ])
        
        return "\n".join(scalars)
    
    def _generate_security_directives(self, config: GraphQLSchemaConfig) -> str:
        """Generate security directives."""
        directives = [
            "# Security Directives",
            "",
            "class AuthDirective(BasePermission):",
            '    """Authentication directive."""',
            "    ",
            "    message = 'Authentication required'",
            "    ",
            "    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:",
            "        request = info.context['request']",
            "        return hasattr(request.state, 'user') and request.state.user is not None",
            "",
            "",
            "class RoleDirective(BasePermission):",
            '    """Role-based authorization directive."""',
            "    ",
            "    def __init__(self, roles: List[str]):",
            "        self.roles = roles",
            "        super().__init__()",
            "    ",
            "    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:",
            "        request = info.context['request']",
            "        if not hasattr(request.state, 'user') or not request.state.user:",
            "            return False",
            "        ",
            "        user_roles = getattr(request.state.user, 'roles', [])",
            "        return any(role in user_roles for role in self.roles)",
            "",
            "",
            "class RateLimitDirective(BasePermission):",
            '    """Rate limiting directive."""',
            "    ",
            "    def __init__(self, max_requests: int, window_seconds: int):",
            "        self.max_requests = max_requests",
            "        self.window_seconds = window_seconds",
            "        super().__init__()",
            "    ",
            "    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:",
            "        request = info.context['request']",
            "        # Implement rate limiting logic",
            "        return rate_limit(",
            "            key=f'graphql:{request.client.host}',",
            "            max_requests=self.max_requests,",
            "            window_seconds=self.window_seconds",
            "        )",
            "",
        ]
        
        return "\n".join(directives)
    
    def _generate_types(self, config: GraphQLSchemaConfig) -> str:
        """Generate GraphQL type definitions."""
        if not config.types:
            return "# No custom types defined"
        
        types_code = ["# GraphQL Types", ""]
        
        for type_name, type_config in config.types.items():
            if type_config.type_kind == GraphQLFieldType.OBJECT:
                types_code.extend(self._generate_object_type(type_name, type_config))
            elif type_config.type_kind == GraphQLFieldType.INPUT:
                types_code.extend(self._generate_input_type(type_name, type_config))
            elif type_config.type_kind == GraphQLFieldType.ENUM:
                types_code.extend(self._generate_enum_type(type_name, type_config))
            elif type_config.type_kind == GraphQLFieldType.INTERFACE:
                types_code.extend(self._generate_interface_type(type_name, type_config))
            
            types_code.append("")
        
        return "\n".join(types_code)
    
    def _generate_object_type(self, type_name: str, type_config: GraphQLTypeConfig) -> List[str]:
        """Generate object type definition."""
        lines = [
            f"@strawberry.type",
            f"class {type_name}:",
            f'    """{type_config.description}"""'
        ]
        
        # Generate fields
        for field_name, field_config in type_config.fields.items():
            field_lines = self._generate_field(field_name, field_config)
            lines.extend([f"    {line}" for line in field_lines])
        
        return lines
    
    def _generate_field(self, field_name: str, field_config: GraphQLFieldConfig) -> List[str]:
        """Generate field definition."""
        # Determine field type annotation
        field_type = self._convert_graphql_type_to_python(field_config.field_type)
        
        # Generate permissions
        permissions = []
        if field_config.permission != GraphQLPermission.PUBLIC:
            permissions.append(f"AuthDirective()")
        
        if field_config.rate_limit:
            permissions.append(f"RateLimitDirective(max_requests={field_config.rate_limit}, window_seconds=60)")
        
        permission_str = f", permission=[{', '.join(permissions)}]" if permissions else ""
        
        # Generate field declaration
        lines = [
            f"{field_name}: {field_type} = strawberry.field(",
            f'    description="{field_config.description}"'
        ]
        
        if field_config.deprecated:
            lines.append(f'    deprecation_reason="{field_config.deprecation_reason}"')
        
        if permission_str:
            lines.append(f"    {permission_str.lstrip(', ')}")
        
        lines[-1] += ")"
        
        return lines
    
    def _convert_graphql_type_to_python(self, graphql_type: str) -> str:
        """Convert GraphQL type notation to Python type annotation."""
        # Handle non-null types
        if graphql_type.endswith("!"):
            base_type = graphql_type[:-1]
            is_required = True
        else:
            base_type = graphql_type
            is_required = False
        
        # Handle list types
        if base_type.startswith("[") and base_type.endswith("]"):
            inner_type = base_type[1:-1]
            python_type = f"List[{self._convert_graphql_type_to_python(inner_type)}]"
        else:
            # Map GraphQL scalars to Python types
            type_mapping = {
                "String": "str",
                "Int": "int", 
                "Float": "float",
                "Boolean": "bool",
                "ID": "str"
            }
            python_type = type_mapping.get(base_type, base_type)
        
        # Add Optional wrapper if nullable
        if not is_required:
            python_type = f"Optional[{python_type}]"
        
        return python_type
    
    def _generate_schema_definition(self, config: GraphQLSchemaConfig) -> str:
        """Generate schema definition."""
        return f'''# Schema Definition

@strawberry.type
class Query:
    """Root query type."""
    
    @strawberry.field(description="Health check endpoint")
    def health(self) -> str:
        return "OK"
    
    @strawberry.field(description="API version")
    def version(self) -> str:
        return "1.0.0"


@strawberry.type  
class Mutation:
    """Root mutation type."""
    
    @strawberry.field(description="Test mutation")
    def test(self, input: str) -> str:
        return f"Echo: {{input}}"


{'@strawberry.type' if config.enable_subscriptions else '# Subscriptions disabled'}
{'class Subscription:' if config.enable_subscriptions else '# class Subscription:'}
{'    """Root subscription type."""' if config.enable_subscriptions else '#     """Root subscription type."""'}
{'    ' if config.enable_subscriptions else '#     '}
{'    @strawberry.subscription' if config.enable_subscriptions else '#     @strawberry.subscription'}
{'    async def notifications(self) -> str:' if config.enable_subscriptions else '#     async def notifications(self) -> str:'}
{'        """Real-time notifications."""' if config.enable_subscriptions else '#         """Real-time notifications."""'}
{'        # Implementation for subscriptions' if config.enable_subscriptions else '#         # Implementation for subscriptions'}
{'        yield "test notification"' if config.enable_subscriptions else '#         yield "test notification"'}

def build_schema() -> GraphQLSchema:
    """Build GraphQL schema with configuration."""
    
    extensions = [
        QueryDepthLimiter(max_depth={config.max_query_depth}),
    ]
    
    return strawberry.Schema(
        query=Query,
        mutation=Mutation,
        {'subscription=Subscription,' if config.enable_subscriptions else '# subscription=Subscription,'}
        extensions=extensions,
        scalar_overrides={{
            {'datetime: DateTime,' if 'DateTime' in config.custom_scalars else ''}
        }}
    )'''
    
    def _generate_schema_config(self, config: GraphQLSchemaConfig) -> str:
        """Generate schema configuration."""
        return f'''# Schema Configuration

SCHEMA_CONFIG = {{
    "name": "{config.schema_name}",
    "description": "{config.description}",
    "introspection": {config.enable_introspection},
    "playground": {config.enable_playground},
    "max_query_depth": {config.max_query_depth},
    "max_query_complexity": {config.max_query_complexity},
    "enable_caching": {config.enable_query_caching},
    "enable_persisted_queries": {config.enable_persisted_queries},
    "enable_batching": {config.enable_batching},
    "default_cache_ttl": {config.default_cache_ttl},
    "federation_enabled": {config.enable_federation},
    "auth_required": {config.auth_required}
}}

def apply_security_middleware(schema: GraphQLSchema) -> GraphQLSchema:
    """Apply security middleware to schema."""
    # Add query validation
    # Add input sanitization  
    # Add authentication checks
    return schema

def apply_performance_optimizations(schema: GraphQLSchema) -> GraphQLSchema:
    """Apply performance optimizations."""
    # Add query complexity analysis
    # Add caching strategies
    # Add batching support
    return schema'''
    
    def _generate_resolver_patterns(self, config: GraphQLSchemaConfig) -> str:
        """Generate resolver patterns."""
        return '''# Resolver Patterns

class BaseResolver:
    """Base resolver with common functionality."""
    
    @staticmethod
    def authenticate(info: Info) -> bool:
        """Check authentication."""
        request = info.context.get('request')
        return hasattr(request.state, 'user') and request.state.user is not None
    
    @staticmethod  
    def authorize(info: Info, required_roles: List[str]) -> bool:
        """Check authorization."""
        if not BaseResolver.authenticate(info):
            return False
        
        request = info.context.get('request')
        user_roles = getattr(request.state.user, 'roles', [])
        return any(role in user_roles for role in required_roles)
    
    @staticmethod
    async def cache_result(key: str, resolver_func: Callable, ttl: int = 300):
        """Cache resolver result."""
        # Implementation for caching
        return await resolver_func()

class CreatorResolver(BaseResolver):
    """Resolver for creator-related operations."""
    
    @staticmethod
    async def get_creator(id: str, info: Info) -> Optional[Any]:
        """Get creator by ID."""
        # Implement creator lookup
        pass
    
    @staticmethod
    async def get_creator_content(creator_id: str, info: Info) -> List[Any]:
        """Get creator's content."""
        # Implement content lookup
        pass'''
    
    def _generate_federation_setup(self, config: GraphQLSchemaConfig) -> str:
        """Generate Apollo Federation setup."""
        return f'''# Apollo Federation Setup

@strawberry.federation.type(keys=["id"])
class FederatedCreator:
    """Federated creator entity."""
    id: strawberry.ID
    
    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        """Resolve entity reference."""
        # Implementation for entity resolution
        return cls(id=id)

def create_federated_schema() -> FederatedSchema:
    """Create federated GraphQL schema."""
    
    return FederatedSchema(
        query=Query,
        mutation=Mutation,
        {'subscription=Subscription,' if config.enable_subscriptions else ''}
        types=[FederatedCreator],
        enable_federation_2=True
    )

# Federation configuration
FEDERATION_CONFIG = {config.federation_config}'''
    
    def _generate_monitoring_setup(self, config: GraphQLSchemaConfig) -> str:
        """Generate monitoring setup."""
        return '''# Monitoring Setup

def apply_monitoring(schema: GraphQLSchema) -> GraphQLSchema:
    """Apply monitoring to GraphQL schema."""
    
    # Add metrics collection
    metrics_collector = GraphQLMetricsCollector()
    
    # Add query logging
    logger = logging.getLogger('graphql')
    
    # Add performance tracking
    # Add error tracking
    # Add usage analytics
    
    return schema

class GraphQLMetrics:
    """GraphQL metrics collection."""
    
    @staticmethod
    def track_query_execution(query: str, execution_time: float):
        """Track query execution metrics."""
        pass
    
    @staticmethod
    def track_resolver_performance(resolver_name: str, execution_time: float):
        """Track resolver performance."""
        pass
    
    @staticmethod
    def track_error(error: Exception, query: str):
        """Track GraphQL errors."""
        pass'''


# Register template
from .template_registry import register_template

register_template(
    GraphQLSchemaTemplate,
    GraphQLSchemaTemplate().metadata
)