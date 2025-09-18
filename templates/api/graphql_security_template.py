"""
🔒 GRAPHQL SECURITY TEMPLATE - ENTERPRISE SECURITY IMPLEMENTATION
================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Enterprise-grade GraphQL security template with:
- Query depth and complexity analysis
- Rate limiting and DDoS protection
- Authentication and authorization
- Input validation and sanitization
- Security directives and middleware
- Audit logging and monitoring

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import hashlib
import re

import strawberry
from strawberry.types import Info
from strawberry.permission import BasePermission
from strawberry.extensions import Extension
from graphql import GraphQLError, DocumentNode
from graphql.language import ast
from pydantic import BaseModel, Field, validator

from ..template_registry import TemplateInterface, TemplateMetadata, TemplateType, TemplateCategory, SecurityLevel

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """GraphQL security levels."""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    AUTHORIZED = "authorized"
    CREATOR = "creator"
    ADMIN = "admin"
    SYSTEM = "system"


class SecurityRule(Enum):
    """Security rule types."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMITING = "rate_limiting"
    QUERY_DEPTH = "query_depth"
    QUERY_COMPLEXITY = "query_complexity"
    INPUT_VALIDATION = "input_validation"
    FIELD_ACCESS = "field_access"
    RESOURCE_ACCESS = "resource_access"


@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    name: str
    rules: List[SecurityRule]
    description: str = ""
    
    # Authentication settings
    require_authentication: bool = True
    allowed_roles: List[str] = field(default_factory=list)
    
    # Rate limiting
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    
    # Query limits
    max_query_depth: int = 10
    max_query_complexity: int = 1000
    
    # Creator economy specific
    creator_resource_access: bool = False
    monetization_required: bool = False


class GraphQLSecurityConfig(BaseModel):
    """Configuration for GraphQL security generation."""
    
    security_name: str = Field(..., description="Name of the security configuration")
    description: str = Field("", description="Security description")
    
    # Global security settings
    global_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enable_introspection": False,
            "enable_playground": False,
            "require_https": True,
            "max_query_depth": 15,
            "max_query_complexity": 2000,
            "default_rate_limit": 100
        }
    )
    
    # Authentication configuration
    auth_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "jwt_secret": "your-secret-key",
            "jwt_algorithm": "HS256",
            "token_expiry": 3600,
            "refresh_token_expiry": 604800,
            "multi_factor_required": False
        }
    )
    
    # Authorization configuration
    authz_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "rbac_enabled": True,
            "default_deny": True,
            "resource_based": True,
            "creator_permissions": ["create", "read", "update", "delete"],
            "admin_permissions": ["*"]
        }
    )
    
    # Security policies
    policies: Dict[str, SecurityPolicy] = Field(default_factory=dict)
    
    # Rate limiting configuration
    rate_limiting: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "storage": "redis",
            "window_size": 60,
            "per_user_limit": 100,
            "per_ip_limit": 200,
            "burst_limit": 150
        }
    )
    
    # Input validation configuration
    validation_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "max_string_length": 10000,
            "max_list_length": 1000,
            "sanitize_html": True,
            "block_sql_injection": True,
            "block_xss": True
        }
    )
    
    # Creator economy security
    creator_security: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enable_creator_validation": True,
            "content_access_control": True,
            "monetization_security": True,
            "collaboration_permissions": True
        }
    )


class GraphQLSecurityTemplate(TemplateInterface):
    """Enterprise GraphQL security template."""
    
    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="graphql_security_template",
            template_type=TemplateType.GRAPHQL,
            category=TemplateCategory.SECURITY,
            version="1.0.0",
            author="Fahed Mlaiel",
            description="Enterprise GraphQL security template with comprehensive protection",
            security_level=SecurityLevel.ENTERPRISE,
            dependencies=["strawberry-graphql", "pyjwt", "redis", "pydantic"],
            tags=["graphql", "security", "authentication", "authorization"],
            compliance_standards=["SOC2", "GDPR", "HIPAA", "PCI-DSS"],
            enterprise_features=[
                "Query depth analysis",
                "Complexity analysis",
                "Rate limiting",
                "Authentication middleware",
                "Authorization directives",
                "Input sanitization",
                "Audit logging"
            ]
        )
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate GraphQL security based on configuration."""
        try:
            security_config = GraphQLSecurityConfig(**config)
            return self._generate_security_code(security_config)
        except Exception as e:
            logger.error(f"Failed to generate GraphQL security: {e}")
            raise
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate security configuration."""
        try:
            GraphQLSecurityConfig(**config)
            return True
        except Exception as e:
            logger.error(f"Invalid GraphQL security config: {e}")
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for configuration."""
        return GraphQLSecurityConfig.schema()
    
    def get_examples(self) -> List[Dict[str, Any]]:
        """Return example configurations."""
        return [
            {
                "security_name": "CreatorEconomySecurity",
                "description": "Security configuration for creator economy GraphQL API",
                "global_settings": {
                    "enable_introspection": False,
                    "enable_playground": False,
                    "max_query_depth": 12,
                    "max_query_complexity": 1500
                },
                "policies": {
                    "creator_policy": {
                        "name": "creator_policy",
                        "rules": ["authentication", "authorization", "rate_limiting"],
                        "description": "Security policy for creator operations",
                        "require_authentication": True,
                        "allowed_roles": ["creator", "admin"],
                        "max_requests_per_minute": 120,
                        "creator_resource_access": True
                    }
                }
            }
        ]
    
    def _generate_security_code(self, config: GraphQLSecurityConfig) -> str:
        """Generate the actual GraphQL security code."""
        
        # Generate imports
        imports = self._generate_imports(config)
        
        # Generate authentication middleware
        auth_middleware = self._generate_authentication_middleware(config)
        
        # Generate authorization directives
        authz_directives = self._generate_authorization_directives(config)
        
        # Generate rate limiting
        rate_limiting = self._generate_rate_limiting(config)
        
        # Generate query analysis
        query_analysis = self._generate_query_analysis(config)
        
        # Generate input validation
        input_validation = self._generate_input_validation(config)
        
        # Generate security extensions
        security_extensions = self._generate_security_extensions(config)
        
        # Generate audit logging
        audit_logging = self._generate_audit_logging(config)
        
        # Generate configuration
        security_config_code = self._generate_security_config(config)
        
        code = f'''"""
{config.security_name} GraphQL Security
Generated by Ainflue GraphQL Security Template

{config.description}

🔒 PROTECTION INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
"""

{imports}

{auth_middleware}

{authz_directives}

{rate_limiting}

{query_analysis}

{input_validation}

{security_extensions}

{audit_logging}

{security_config_code}

# Security factory
def create_security_middleware() -> GraphQLSecurityMiddleware:
    """Create security middleware with configuration."""
    middleware = GraphQLSecurityMiddleware()
    
    # Apply security policies
    middleware = apply_security_policies(middleware)
    
    # Apply monitoring
    middleware = apply_security_monitoring(middleware)
    
    return middleware

# Export security middleware
security_middleware = create_security_middleware()

if __name__ == "__main__":
    print(f"✅ {config.security_name} initialized successfully")
    print(f"📊 Security statistics:")
    print(f"   - Policies: {len(config.policies)}")
    print(f"   - Max query depth: {config.global_settings['max_query_depth']}")
    print(f"   - Max complexity: {config.global_settings['max_query_complexity']}")
    print(f"   - Rate limiting: {config.rate_limiting['enabled']}")
'''
        
        return code
    
    def _generate_imports(self, config: GraphQLSecurityConfig) -> str:
        """Generate import statements."""
        return '''from typing import Dict, List, Optional, Any, Callable, Set, Union
from datetime import datetime, timedelta
import logging
import hashlib
import re
import jwt
from functools import wraps

import strawberry
from strawberry.types import Info
from strawberry.permission import BasePermission
from strawberry.extensions import Extension
from graphql import GraphQLError, DocumentNode, validate, ValidationRule
from graphql.language import ast
from graphql.execution import MiddlewareManager

from fastapi import Request, HTTPException, status
from pydantic import BaseModel
import redis.asyncio as redis

# Core imports
from core.auth import get_current_user, verify_token
from core.rate_limiting import rate_limit
from monitoring.security_metrics import SecurityMetricsCollector
from utils.validation import sanitize_input, validate_graphql_input
from utils.security import detect_sql_injection, detect_xss

logger = logging.getLogger(__name__)'''
    
    def _generate_authentication_middleware(self, config: GraphQLSecurityConfig) -> str:
        """Generate authentication middleware."""
        auth_config = config.auth_config
        
        return f'''# Authentication Middleware

class GraphQLAuthenticationMiddleware:
    """GraphQL authentication middleware."""
    
    def __init__(self):
        self.jwt_secret = "{auth_config['jwt_secret']}"
        self.jwt_algorithm = "{auth_config['jwt_algorithm']}"
        self.token_expiry = {auth_config['token_expiry']}
        self.require_mfa = {auth_config['multi_factor_required']}
    
    async def authenticate_request(self, info: Info) -> Optional[Dict[str, Any]]:
        """Authenticate GraphQL request."""
        request = info.context.get('request')
        if not request:
            return None
        
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        try:
            # Verify JWT token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            
            # Check token expiry
            if datetime.fromtimestamp(payload.get('exp', 0)) < datetime.now():
                raise GraphQLError("Token expired")
            
            # Get user information
            user_id = payload.get('user_id')
            if not user_id:
                raise GraphQLError("Invalid token payload")
            
            # Load user data (implementation specific)
            user_data = await self._load_user_data(user_id)
            if not user_data:
                raise GraphQLError("User not found")
            
            # Check MFA if required
            if self.require_mfa and not payload.get('mfa_verified'):
                raise GraphQLError("Multi-factor authentication required")
            
            return user_data
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {{e}}")
            raise GraphQLError("Invalid authentication token")
        except Exception as e:
            logger.error(f"Authentication error: {{e}}")
            raise GraphQLError("Authentication failed")
    
    async def _load_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load user data from database."""
        # Implementation specific to your user model
        return {{
            "id": user_id,
            "roles": ["user"],  # Load from database
            "permissions": [],  # Load from database
            "is_creator": False,  # Load from database
            "creator_id": None  # Load from database
        }}

class AuthenticationRequired(BasePermission):
    """Permission class requiring authentication."""
    
    message = "Authentication required"
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        user = info.context.get('user')
        return user is not None

class RoleRequired(BasePermission):
    """Permission class requiring specific roles."""
    
    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles
        self.message = f"Required roles: {{', '.join(required_roles)}}"
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        user = info.context.get('user')
        if not user:
            return False
        
        user_roles = user.get('roles', [])
        return any(role in user_roles for role in self.required_roles)

class CreatorRequired(BasePermission):
    """Permission class requiring creator status."""
    
    message = "Creator access required"
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        user = info.context.get('user')
        if not user:
            return False
        
        return user.get('is_creator', False)'''
    
    def _generate_authorization_directives(self, config: GraphQLSecurityConfig) -> str:
        """Generate authorization directives."""
        return '''# Authorization Directives

class ResourceAccessPermission(BasePermission):
    """Permission for resource-based access control."""
    
    def __init__(self, resource_type: str, action: str):
        self.resource_type = resource_type
        self.action = action
        self.message = f"Permission denied for {action} on {resource_type}"
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        user = info.context.get('user')
        if not user:
            return False
        
        # Check admin privileges
        if 'admin' in user.get('roles', []):
            return True
        
        # Resource-specific logic
        if self.resource_type == 'content':
            return self._check_content_access(user, source, self.action)
        elif self.resource_type == 'creator':
            return self._check_creator_access(user, source, self.action)
        elif self.resource_type == 'collaboration':
            return self._check_collaboration_access(user, source, self.action)
        
        return False
    
    def _check_content_access(self, user: Dict[str, Any], content: Any, action: str) -> bool:
        """Check content access permissions."""
        if not content:
            return action == 'create'
        
        # Creator can access their own content
        if hasattr(content, 'creator_id') and str(content.creator_id) == str(user.get('id')):
            return True
        
        # Check collaboration permissions
        if action == 'read' and hasattr(content, 'is_public') and content.is_public:
            return True
        
        return False
    
    def _check_creator_access(self, user: Dict[str, Any], creator: Any, action: str) -> bool:
        """Check creator access permissions."""
        if not creator:
            return action == 'create' and user.get('is_creator', False)
        
        # Creator can access their own profile
        if hasattr(creator, 'id') and str(creator.id) == str(user.get('creator_id')):
            return True
        
        # Public read access
        if action == 'read':
            return True
        
        return False
    
    def _check_collaboration_access(self, user: Dict[str, Any], collaboration: Any, action: str) -> bool:
        """Check collaboration access permissions."""
        if not collaboration:
            return action == 'create' and user.get('is_creator', False)
        
        # Participants can access collaboration
        if hasattr(collaboration, 'participants'):
            participant_ids = [str(p.id) for p in collaboration.participants]
            if str(user.get('id')) in participant_ids:
                return True
        
        return False

class MonetizationRequired(BasePermission):
    """Permission requiring monetization access."""
    
    message = "Monetization access required"
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        user = info.context.get('user')
        if not user:
            return False
        
        # Check if user has monetization enabled
        return user.get('monetization_enabled', False)'''
    
    def _generate_rate_limiting(self, config: GraphQLSecurityConfig) -> str:
        """Generate rate limiting implementation."""
        rate_config = config.rate_limiting
        
        return f'''# Rate Limiting

class GraphQLRateLimiter:
    """GraphQL rate limiting implementation."""
    
    def __init__(self):
        self.enabled = {rate_config['enabled']}
        self.window_size = {rate_config['window_size']}
        self.per_user_limit = {rate_config['per_user_limit']}
        self.per_ip_limit = {rate_config['per_ip_limit']}
        self.burst_limit = {rate_config['burst_limit']}
        
        # Initialize Redis client for rate limiting
        self.redis_client = None
    
    async def check_rate_limit(self, info: Info, operation_name: str) -> bool:
        """Check if request is within rate limits."""
        if not self.enabled:
            return True
        
        request = info.context.get('request')
        if not request:
            return True
        
        # Get user identifier
        user = info.context.get('user')
        user_id = user.get('id') if user else None
        ip_address = request.client.host
        
        # Check user-based rate limit
        if user_id:
            user_key = f"rate_limit:user:{{user_id}}:{{operation_name}}"
            if not await self._check_limit(user_key, self.per_user_limit):
                logger.warning(f"Rate limit exceeded for user {{user_id}} on {{operation_name}}")
                raise GraphQLError("Rate limit exceeded")
        
        # Check IP-based rate limit
        ip_key = f"rate_limit:ip:{{ip_address}}:{{operation_name}}"
        if not await self._check_limit(ip_key, self.per_ip_limit):
            logger.warning(f"Rate limit exceeded for IP {{ip_address}} on {{operation_name}}")
            raise GraphQLError("Rate limit exceeded")
        
        return True
    
    async def _check_limit(self, key: str, limit: int) -> bool:
        """Check rate limit for a specific key."""
        if not self.redis_client:
            # Initialize Redis client
            self.redis_client = redis.Redis.from_url("redis://localhost:6379")
        
        try:
            # Sliding window rate limiting
            now = datetime.now().timestamp()
            window_start = now - self.window_size
            
            # Remove old entries
            await self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_count = await self.redis_client.zcard(key)
            
            if current_count >= limit:
                return False
            
            # Add current request
            await self.redis_client.zadd(key, {{str(now): now}})
            await self.redis_client.expire(key, self.window_size)
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting error: {{e}}")
            # Fail open - allow request if rate limiting fails
            return True

class RateLimitExtension(Extension):
    """GraphQL extension for rate limiting."""
    
    def __init__(self):
        self.rate_limiter = GraphQLRateLimiter()
    
    async def on_request_start(self):
        """Check rate limits before request execution."""
        operation_name = self.execution_context.operation_name or "unknown"
        await self.rate_limiter.check_rate_limit(
            self.execution_context.context.get('info'),
            operation_name
        )'''
    
    def _generate_query_analysis(self, config: GraphQLSecurityConfig) -> str:
        """Generate query depth and complexity analysis."""
        global_settings = config.global_settings
        
        return f'''# Query Analysis

class QueryDepthAnalyzer:
    """Analyze GraphQL query depth."""
    
    def __init__(self, max_depth: int = {global_settings['max_query_depth']}):
        self.max_depth = max_depth
    
    def analyze_depth(self, document: DocumentNode) -> int:
        """Calculate query depth."""
        max_depth = 0
        
        for definition in document.definitions:
            if isinstance(definition, ast.OperationDefinitionNode):
                depth = self._calculate_selection_depth(definition.selection_set, 0)
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _calculate_selection_depth(self, selection_set: ast.SelectionSetNode, current_depth: int) -> int:
        """Recursively calculate selection depth."""
        if not selection_set or not selection_set.selections:
            return current_depth
        
        max_depth = current_depth
        
        for selection in selection_set.selections:
            if isinstance(selection, ast.FieldNode):
                depth = current_depth + 1
                if selection.selection_set:
                    depth = self._calculate_selection_depth(selection.selection_set, depth)
                max_depth = max(max_depth, depth)
            elif isinstance(selection, ast.InlineFragmentNode):
                depth = self._calculate_selection_depth(selection.selection_set, current_depth)
                max_depth = max(max_depth, depth)
            elif isinstance(selection, ast.FragmentSpreadNode):
                # Fragment spreads would need fragment definition lookup
                # For simplicity, add 1 to current depth
                max_depth = max(max_depth, current_depth + 1)
        
        return max_depth
    
    def validate_depth(self, document: DocumentNode) -> bool:
        """Validate query depth."""
        actual_depth = self.analyze_depth(document)
        if actual_depth > self.max_depth:
            raise GraphQLError(f"Query depth {{actual_depth}} exceeds maximum allowed depth {{self.max_depth}}")
        return True

class QueryComplexityAnalyzer:
    """Analyze GraphQL query complexity."""
    
    def __init__(self, max_complexity: int = {global_settings['max_query_complexity']}):
        self.max_complexity = max_complexity
        self.field_costs = {{
            # Define field complexity costs
            'creator': 1,
            'content': 2,
            'collaboration': 3,
            'analytics': 5,
            'monetization': 3
        }}
    
    def analyze_complexity(self, document: DocumentNode) -> int:
        """Calculate query complexity."""
        total_complexity = 0
        
        for definition in document.definitions:
            if isinstance(definition, ast.OperationDefinitionNode):
                complexity = self._calculate_selection_complexity(definition.selection_set)
                total_complexity += complexity
        
        return total_complexity
    
    def _calculate_selection_complexity(self, selection_set: ast.SelectionSetNode) -> int:
        """Recursively calculate selection complexity."""
        if not selection_set or not selection_set.selections:
            return 0
        
        total_complexity = 0
        
        for selection in selection_set.selections:
            if isinstance(selection, ast.FieldNode):
                field_name = selection.name.value
                field_cost = self.field_costs.get(field_name, 1)
                
                # Add complexity for nested selections
                if selection.selection_set:
                    nested_complexity = self._calculate_selection_complexity(selection.selection_set)
                    field_cost *= max(1, nested_complexity)
                
                total_complexity += field_cost
            elif isinstance(selection, ast.InlineFragmentNode):
                complexity = self._calculate_selection_complexity(selection.selection_set)
                total_complexity += complexity
        
        return total_complexity
    
    def validate_complexity(self, document: DocumentNode) -> bool:
        """Validate query complexity."""
        actual_complexity = self.analyze_complexity(document)
        if actual_complexity > self.max_complexity:
            raise GraphQLError(f"Query complexity {{actual_complexity}} exceeds maximum allowed complexity {{self.max_complexity}}")
        return True

class QueryAnalysisExtension(Extension):
    """GraphQL extension for query analysis."""
    
    def __init__(self):
        self.depth_analyzer = QueryDepthAnalyzer()
        self.complexity_analyzer = QueryComplexityAnalyzer()
    
    async def on_request_start(self):
        """Analyze query before execution."""
        document = self.execution_context.query
        
        # Validate query depth
        self.depth_analyzer.validate_depth(document)
        
        # Validate query complexity
        self.complexity_analyzer.validate_complexity(document)'''
    
    def _generate_input_validation(self, config: GraphQLSecurityConfig) -> str:
        """Generate input validation implementation."""
        validation_config = config.validation_config
        
        return f'''# Input Validation

class GraphQLInputValidator:
    """GraphQL input validation and sanitization."""
    
    def __init__(self):
        self.max_string_length = {validation_config['max_string_length']}
        self.max_list_length = {validation_config['max_list_length']}
        self.sanitize_html = {validation_config['sanitize_html']}
        self.block_sql_injection = {validation_config['block_sql_injection']}
        self.block_xss = {validation_config['block_xss']}
    
    def validate_input(self, value: Any, field_name: str = "") -> Any:
        """Validate and sanitize input value."""
        if value is None:
            return value
        
        if isinstance(value, str):
            return self._validate_string(value, field_name)
        elif isinstance(value, list):
            return self._validate_list(value, field_name)
        elif isinstance(value, dict):
            return self._validate_dict(value, field_name)
        
        return value
    
    def _validate_string(self, value: str, field_name: str) -> str:
        """Validate string input."""
        # Check length
        if len(value) > self.max_string_length:
            raise GraphQLError(f"String too long for field {{field_name}}: {{len(value)}} > {{self.max_string_length}}")
        
        # Check for SQL injection
        if self.block_sql_injection and detect_sql_injection(value):
            logger.warning(f"SQL injection attempt detected in field {{field_name}}: {{value[:100]}}")
            raise GraphQLError("Invalid input detected")
        
        # Check for XSS
        if self.block_xss and detect_xss(value):
            logger.warning(f"XSS attempt detected in field {{field_name}}: {{value[:100]}}")
            raise GraphQLError("Invalid input detected")
        
        # Sanitize HTML if enabled
        if self.sanitize_html:
            value = sanitize_input(value)
        
        return value
    
    def _validate_list(self, value: List[Any], field_name: str) -> List[Any]:
        """Validate list input."""
        # Check length
        if len(value) > self.max_list_length:
            raise GraphQLError(f"List too long for field {{field_name}}: {{len(value)}} > {{self.max_list_length}}")
        
        # Validate each item
        return [self.validate_input(item, f"{{field_name}}[{{i}}]") for i, item in enumerate(value)]
    
    def _validate_dict(self, value: Dict[str, Any], field_name: str) -> Dict[str, Any]:
        """Validate dictionary input."""
        return {{k: self.validate_input(v, f"{{field_name}}.{{k}}") for k, v in value.items()}}

class InputValidationExtension(Extension):
    """GraphQL extension for input validation."""
    
    def __init__(self):
        self.validator = GraphQLInputValidator()
    
    async def on_request_start(self):
        """Validate inputs before execution."""
        # Get variables from request
        variables = self.execution_context.variable_values or {{}}
        
        # Validate each variable
        for var_name, var_value in variables.items():
            self.validator.validate_input(var_value, var_name)'''
    
    def _generate_security_extensions(self, config: GraphQLSecurityConfig) -> str:
        """Generate security extensions."""
        return '''# Security Extensions

class SecurityExtension(Extension):
    """Comprehensive security extension."""
    
    def __init__(self):
        self.auth_middleware = GraphQLAuthenticationMiddleware()
        self.rate_limiter = GraphQLRateLimiter()
        self.query_analyzer = QueryAnalysisExtension()
        self.input_validator = InputValidationExtension()
        self.audit_logger = SecurityAuditLogger()
    
    async def on_request_start(self):
        """Execute security checks before request."""
        info = self.execution_context.context.get('info')
        
        # Authenticate user
        user = await self.auth_middleware.authenticate_request(info)
        if user:
            self.execution_context.context['user'] = user
        
        # Check rate limits
        await self.rate_limiter.check_rate_limit(
            info,
            self.execution_context.operation_name or "unknown"
        )
        
        # Analyze query
        await self.query_analyzer.on_request_start()
        
        # Validate inputs
        await self.input_validator.on_request_start()
        
        # Log request
        await self.audit_logger.log_request_start(
            self.execution_context.query,
            self.execution_context.variable_values,
            user
        )
    
    async def on_request_end(self):
        """Execute security actions after request."""
        # Log request completion
        await self.audit_logger.log_request_end(
            self.execution_context.result,
            self.execution_context.errors
        )

class GraphQLSecurityMiddleware:
    """Main GraphQL security middleware."""
    
    def __init__(self):
        self.security_extension = SecurityExtension()
        self.security_policies = {{}}
    
    def apply_to_schema(self, schema):
        """Apply security middleware to schema."""
        # Add security extensions
        schema.extensions = [self.security_extension]
        
        return schema
    
    def add_security_policy(self, name: str, policy: SecurityPolicy):
        """Add security policy."""
        self.security_policies[name] = policy
    
    def get_security_context(self, request: Request) -> Dict[str, Any]:
        """Get security context for request."""
        return {{
            'request': request,
            'security_policies': self.security_policies,
            'timestamp': datetime.now()
        }}'''
    
    def _generate_audit_logging(self, config: GraphQLSecurityConfig) -> str:
        """Generate audit logging implementation."""
        return '''# Security Audit Logging

class SecurityAuditLogger:
    """Security audit logging for GraphQL."""
    
    def __init__(self):
        self.logger = logging.getLogger('security.audit')
        self.metrics_collector = SecurityMetricsCollector()
    
    async def log_request_start(
        self,
        query: DocumentNode,
        variables: Optional[Dict[str, Any]],
        user: Optional[Dict[str, Any]]
    ):
        """Log GraphQL request start."""
        log_data = {
            'event': 'graphql_request_start',
            'timestamp': datetime.now().isoformat(),
            'user_id': user.get('id') if user else None,
            'query_hash': self._hash_query(query),
            'has_variables': bool(variables),
            'variable_count': len(variables) if variables else 0
        }
        
        self.logger.info("GraphQL request started", extra=log_data)
        
        # Update metrics
        await self.metrics_collector.increment_request_count(
            user.get('id') if user else 'anonymous'
        )
    
    async def log_request_end(
        self,
        result: Any,
        errors: Optional[List[Any]]
    ):
        """Log GraphQL request completion."""
        log_data = {
            'event': 'graphql_request_end',
            'timestamp': datetime.now().isoformat(),
            'has_errors': bool(errors),
            'error_count': len(errors) if errors else 0,
            'has_data': bool(result and result.data)
        }
        
        if errors:
            log_data['error_types'] = [type(error).__name__ for error in errors]
            self.logger.warning("GraphQL request completed with errors", extra=log_data)
            
            # Update error metrics
            await self.metrics_collector.increment_error_count(errors)
        else:
            self.logger.info("GraphQL request completed successfully", extra=log_data)
    
    async def log_security_violation(
        self,
        violation_type: str,
        details: Dict[str, Any],
        user: Optional[Dict[str, Any]] = None
    ):
        """Log security violation."""
        log_data = {
            'event': 'security_violation',
            'violation_type': violation_type,
            'timestamp': datetime.now().isoformat(),
            'user_id': user.get('id') if user else None,
            'details': details
        }
        
        self.logger.warning("Security violation detected", extra=log_data)
        
        # Update security metrics
        await self.metrics_collector.increment_security_violation_count(violation_type)
    
    def _hash_query(self, query: DocumentNode) -> str:
        """Generate hash for GraphQL query."""
        query_string = str(query)
        return hashlib.sha256(query_string.encode()).hexdigest()[:16]'''
    
    def _generate_security_config(self, config: GraphQLSecurityConfig) -> str:
        """Generate security configuration."""
        return f'''# Security Configuration

SECURITY_CONFIG = {config.dict()}

def apply_security_policies(middleware: GraphQLSecurityMiddleware) -> GraphQLSecurityMiddleware:
    """Apply security policies to middleware."""
    for policy_name, policy_config in SECURITY_CONFIG['policies'].items():
        policy = SecurityPolicy(**policy_config)
        middleware.add_security_policy(policy_name, policy)
    
    return middleware

def apply_security_monitoring(middleware: GraphQLSecurityMiddleware) -> GraphQLSecurityMiddleware:
    """Apply security monitoring."""
    # Add security metrics collection
    # Add threat detection
    # Add anomaly detection
    return middleware

def create_security_context(request: Request) -> Dict[str, Any]:
    """Create security context for GraphQL request."""
    return {{
        'request': request,
        'security_config': SECURITY_CONFIG,
        'timestamp': datetime.now(),
        'user_agent': request.headers.get('User-Agent'),
        'ip_address': request.client.host
    }}'''


# Register template
from .template_registry import register_template

register_template(
    GraphQLSecurityTemplate,
    GraphQLSecurityTemplate().metadata
)