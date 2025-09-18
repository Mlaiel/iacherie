"""
🔒 GRAPHQL FEDERATION TEMPLATE - APOLLO FEDERATION IMPLEMENTATION
================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Enterprise-grade Apollo Federation template with:
- Federation v2 support
- Entity resolution
- Schema composition
- Gateway configuration
- Service discovery

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

import strawberry
from strawberry.federation import Schema as FederatedSchema
from strawberry.federation.schema_directives import Key, External, Requires, Provides
from pydantic import BaseModel, Field

from ..template_registry import TemplateInterface, TemplateMetadata, TemplateType, TemplateCategory, SecurityLevel

logger = logging.getLogger(__name__)


class GraphQLFederationConfig(BaseModel):
    """Configuration for GraphQL federation generation."""
    
    service_name: str = Field(..., description="Name of the federated service")
    service_url: str = Field(..., description="URL of the federated service")
    description: str = Field("", description="Federation description")
    
    # Federation configuration
    federation_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "version": "2.0",
            "enable_entity_cache": True,
            "enable_composition": True,
            "gateway_url": "http://localhost:4000/graphql"
        }
    )
    
    # Entity configuration
    entities: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Federated entities configuration"
    )
    
    # Service configuration
    service_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "port": 4001,
            "health_check": True,
            "metrics_enabled": True,
            "tracing_enabled": True
        }
    )


class GraphQLFederationTemplate(TemplateInterface):
    """Enterprise GraphQL federation template."""
    
    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="graphql_federation_template",
            template_type=TemplateType.GRAPHQL,
            category=TemplateCategory.INFRASTRUCTURE,
            version="1.0.0",
            author="Fahed Mlaiel",
            description="Enterprise GraphQL federation template with Apollo Federation v2",
            security_level=SecurityLevel.ENTERPRISE,
            dependencies=["strawberry-graphql", "strawberry-federation"],
            tags=["graphql", "federation", "apollo", "microservices"],
            enterprise_features=[
                "Apollo Federation v2",
                "Entity resolution",
                "Schema composition",
                "Service discovery",
                "Gateway configuration"
            ]
        )
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate GraphQL federation based on configuration."""
        try:
            federation_config = GraphQLFederationConfig(**config)
            return self._generate_federation_code(federation_config)
        except Exception as e:
            logger.error(f"Failed to generate GraphQL federation: {e}")
            raise
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate federation configuration."""
        try:
            GraphQLFederationConfig(**config)
            return True
        except Exception as e:
            logger.error(f"Invalid GraphQL federation config: {e}")
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for configuration."""
        return GraphQLFederationConfig.schema()
    
    def get_examples(self) -> List[Dict[str, Any]]:
        """Return example configurations."""
        return [
            {
                "service_name": "creator-service",
                "service_url": "http://localhost:4001/graphql",
                "description": "Creator economy federated service",
                "entities": {
                    "Creator": {
                        "key_fields": ["id"],
                        "external_fields": [],
                        "provides": ["username", "avatar"],
                        "requires": []
                    },
                    "Content": {
                        "key_fields": ["id", "creator { id }"],
                        "external_fields": ["creator"],
                        "provides": ["title", "description"],
                        "requires": ["creator { username }"]
                    }
                }
            }
        ]
    
    def _generate_federation_code(self, config: GraphQLFederationConfig) -> str:
        """Generate the actual GraphQL federation code."""
        
        # Generate imports
        imports = self._generate_imports()
        
        # Generate federated entities
        entities = self._generate_federated_entities(config)
        
        # Generate federation schema
        federation_schema = self._generate_federation_schema(config)
        
        # Generate gateway configuration
        gateway_config = self._generate_gateway_config(config)
        
        # Generate service setup
        service_setup = self._generate_service_setup(config)
        
        code = f'''"""
{config.service_name} GraphQL Federation
Generated by Ainflue GraphQL Federation Template

{config.description}

🔒 PROTECTION INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
"""

{imports}

{entities}

{federation_schema}

{gateway_config}

{service_setup}

if __name__ == "__main__":
    print(f"✅ {config.service_name} federation service initialized")
    print(f"📊 Federation statistics:")
    print(f"   - Service: {config.service_name}")
    print(f"   - URL: {config.service_url}")
    print(f"   - Entities: {len(config.entities)}")
    print(f"   - Federation version: {config.federation_config['version']}")
'''
        
        return code
    
    def _generate_imports(self) -> str:
        """Generate import statements."""
        return '''from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging

import strawberry
from strawberry.federation import Schema as FederatedSchema
from strawberry.federation.schema_directives import Key, External, Requires, Provides, Override
from strawberry.types import Info

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

logger = logging.getLogger(__name__)'''
    
    def _generate_federated_entities(self, config: GraphQLFederationConfig) -> str:
        """Generate federated entity definitions."""
        if not config.entities:
            return "# No federated entities defined"
        
        entities_code = ["# Federated Entities", ""]
        
        for entity_name, entity_config in config.entities.items():
            key_fields = entity_config.get("key_fields", ["id"])
            external_fields = entity_config.get("external_fields", [])
            
            # Generate entity class
            entities_code.extend([
                f"@strawberry.federation.type(",
                f"    keys={key_fields}",
                f")",
                f"class {entity_name}:",
                f'    """{entity_name} federated entity."""',
                ""
            ])
            
            # Generate key fields
            for field in key_fields:
                if field in external_fields:
                    entities_code.append(f"    {field}: str = strawberry.federation.field(external=True)")
                else:
                    entities_code.append(f"    {field}: str")
            
            entities_code.extend([
                "",
                f"    @classmethod",
                f"    def resolve_reference(cls, **data):",
                f'        """Resolve {entity_name} reference."""',
                f"        # Implementation specific to {entity_name}",
                f"        entity_id = data.get('id')",
                f"        if entity_id:",
                f"            return cls(id=entity_id)",
                f"        return None",
                "",
                ""
            ])
        
        return "\n".join(entities_code)
    
    def _generate_federation_schema(self, config: GraphQLFederationConfig) -> str:
        """Generate federation schema definition."""
        entity_types = list(config.entities.keys()) if config.entities else []
        
        return f'''# Federation Schema

@strawberry.type
class Query:
    """Federated query type."""
    
    @strawberry.field
    def service_info(self) -> str:
        """Get service information."""
        return "{config.service_name} v1.0.0"
    
    @strawberry.field
    def health(self) -> str:
        """Health check endpoint."""
        return "OK"

@strawberry.type
class Mutation:
    """Federated mutation type."""
    
    @strawberry.field
    def ping(self, message: str) -> str:
        """Ping mutation for testing."""
        return f"Pong: {{message}}"

# Create federated schema
federated_schema = FederatedSchema(
    query=Query,
    mutation=Mutation,
    types={entity_types if entity_types else []},
    enable_federation_2={config.federation_config.get('version') == '2.0'}
)

# Export SDL for gateway
def get_federated_sdl() -> str:
    """Get federated schema definition language."""
    return federated_schema.sdl'''
    
    def _generate_gateway_config(self, config: GraphQLFederationConfig) -> str:
        """Generate gateway configuration."""
        return f'''# Gateway Configuration

GATEWAY_CONFIG = {{
    "name": "{config.service_name}",
    "url": "{config.service_url}",
    "sdl_url": "{config.service_url}/sdl",
    "health_check_url": "{config.service_url}/health",
    "enable_subscription": {config.federation_config.get('enable_subscriptions', False)},
    "enable_introspection": {config.federation_config.get('enable_introspection', False)},
    "federation_version": "{config.federation_config.get('version', '2.0')}"
}}

def register_with_gateway():
    """Register service with federation gateway."""
    import httpx
    
    gateway_url = "{config.federation_config.get('gateway_url', 'http://localhost:4000')}"
    registration_data = {{
        "name": GATEWAY_CONFIG["name"],
        "url": GATEWAY_CONFIG["url"],
        "sdl": get_federated_sdl()
    }}
    
    try:
        response = httpx.post(
            f"{{gateway_url}}/register-service",
            json=registration_data,
            timeout=10
        )
        if response.status_code == 200:
            logger.info(f"Successfully registered {{GATEWAY_CONFIG['name']}} with gateway")
        else:
            logger.error(f"Failed to register with gateway: {{response.status_code}}")
    except Exception as e:
        logger.error(f"Gateway registration error: {{e}}")'''
    
    def _generate_service_setup(self, config: GraphQLFederationConfig) -> str:
        """Generate service setup and startup."""
        port = config.service_config.get('port', 4001)
        
        return f'''# Service Setup

app = FastAPI(
    title="{config.service_name}",
    description="{config.description}",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GraphQL endpoint
from strawberry.fastapi import GraphQLRouter

graphql_router = GraphQLRouter(
    federated_schema,
    path="/graphql",
    graphiql={config.federation_config.get('enable_playground', False)}
)

app.include_router(graphql_router)

# Add federation endpoints
@app.get("/sdl")
async def get_sdl():
    """Get federated SDL."""
    return {{"sdl": get_federated_sdl()}}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {{"status": "healthy", "service": "{config.service_name}"}}

@app.get("/federation-config")
async def get_federation_config():
    """Get federation configuration."""
    return GATEWAY_CONFIG

# Startup event
@app.on_event("startup")
async def startup_event():
    """Service startup."""
    logger.info(f"Starting {{app.title}} on port {port}")
    
    # Register with gateway
    if {config.federation_config.get('enable_composition', True)}:
        register_with_gateway()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Service shutdown."""
    logger.info(f"Shutting down {{app.title}}")

def run_service():
    """Run the federated service."""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port={port},
        reload=False,
        log_level="info"
    )'''


# Register template
from .template_registry import register_template

register_template(
    GraphQLFederationTemplate,
    GraphQLFederationTemplate().metadata
)