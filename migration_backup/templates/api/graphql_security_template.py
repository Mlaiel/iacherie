"""GraphQL Security Template for IA Chéries Platform
Enterprise-grade GraphQL security with comprehensive protection mechanisms

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
import hashlib
import time
from typing import Dict, Any, Optional, List, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import re

from graphql import GraphQLError, GraphQLResolveInfo, DocumentNode, OperationDefinitionNode
from graphql.language import ast
from graphql.validation import ValidationRule
from graphql.execution.middleware import Middleware
from graphql.error import GraphQLError

from core.config import get_settings
from core.auth import get_current_user, verify_permissions, decode_jwt_token
from core.rate_limiting import RateLimiter
from core.logging import log_security_event
from utils.exceptions import SecurityException, AuthenticationException
from monitoring.security_metrics import GraphQLSecurityMetrics

logger = logging.getLogger(__name__)
settings = get_settings()


class SecurityThreatLevel(Enum):
    """Security threat level classifications"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityViolation:
    """Security violation record"""
    violation_type: str
    threat_level: SecurityThreatLevel
    user_id: Optional[str]
    ip_address: str
    query: str
    timestamp: datetime
    metadata: Dict[str, Any]


class QueryComplexityAnalyzer:
    """Analyzes GraphQL query complexity to prevent DoS attacks"""
    
    def __init__(self, max_complexity: int = 1000, max_depth: int = 10):
        self.max_complexity = max_complexity
        self.max_depth = max_depth
        self.field_complexity_map = self._build_complexity_map()
    
    def _build_complexity_map(self) -> Dict[str, int]:
        """Build field complexity mapping"""
        return {
            # Simple fields
            "id": 1,
            "name": 1,
            "description": 1,
            "status": 1,
            "created_at": 1,
            "updated_at": 1,
            
            # Complex fields
            "search": 20,
            "analytics": 15,
            "relations": 10,
            "collaborations": 10,
            
            # Expensive operations
            "aggregations": 50,
            "full_text_search": 30,
            "advanced_analytics": 100,
            
            # Connection fields (multiplied by first/last argument)
            "list": 5,
            "connection": 5,
        }
    
    def analyze_query(self, document: DocumentNode) -> Dict[str, Any]:
        """Analyze query complexity and depth"""
        complexity = 0
        max_depth = 0
        
        for definition in document.definitions:
            if isinstance(definition, OperationDefinitionNode):
                query_complexity, query_depth = self._analyze_selection_set(
                    definition.selection_set, 1
                )
                complexity += query_complexity
                max_depth = max(max_depth, query_depth)
        
        return {
            "complexity": complexity,
            "depth": max_depth,
            "is_valid": complexity <= self.max_complexity and max_depth <= self.max_depth,
            "violations": self._get_violations(complexity, max_depth)
        }
    
    def _analyze_selection_set(self, selection_set, current_depth: int) -> tuple:
        """Recursively analyze selection set complexity"""
        complexity = 0
        max_depth = current_depth
        
        for selection in selection_set.selections:
            if hasattr(selection, 'name'):
                field_name = selection.name.value
                field_complexity = self.field_complexity_map.get(field_name, 1)
                
                # Handle list/connection multipliers
                if field_name in ['list', 'connection'] and selection.arguments:
                    multiplier = self._get_list_multiplier(selection.arguments)
                    field_complexity *= multiplier
                
                complexity += field_complexity
                
                # Recursively analyze nested selections
                if selection.selection_set:
                    nested_complexity, nested_depth = self._analyze_selection_set(
                        selection.selection_set, current_depth + 1
                    )
                    complexity += nested_complexity
                    max_depth = max(max_depth, nested_depth)
        
        return complexity, max_depth
    
    def _get_list_multiplier(self, arguments) -> int:
        """Get list multiplier from first/last arguments"""
        for arg in arguments:
            if arg.name.value in ['first', 'last', 'limit']:
                if hasattr(arg.value, 'value'):
                    return min(arg.value.value, 100)  # Cap at 100
        return 10  # Default multiplier
    
    def _get_violations(self, complexity: int, depth: int) -> List[str]:
        """Get list of violations"""
        violations = []
        if complexity > self.max_complexity:
            violations.append(f"Query complexity {complexity} exceeds limit {self.max_complexity}")
        if depth > self.max_depth:
            violations.append(f"Query depth {depth} exceeds limit {self.max_depth}")
        return violations


class GraphQLSecurityMiddleware(Middleware):
    """Comprehensive GraphQL security middleware"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.complexity_analyzer = QueryComplexityAnalyzer()
        self.blocked_ips: Set[str] = set()
        self.suspicious_patterns = self._compile_suspicious_patterns()
        self.metrics = GraphQLSecurityMetrics()
    
    def _compile_suspicious_patterns(self) -> List[re.Pattern]:
        """Compile suspicious query patterns"""
        patterns = [
            # Introspection abuse
            re.compile(r'__schema.*types.*fields', re.IGNORECASE),
            re.compile(r'__type.*name.*fields', re.IGNORECASE),
            
            # Common injection attempts
            re.compile(r'union.*select.*from', re.IGNORECASE),
            re.compile(r'script.*alert.*xss', re.IGNORECASE),
            re.compile(r'javascript.*void.*0', re.IGNORECASE),
            
            # Mass data extraction patterns
            re.compile(r'(\w+)\s*{\s*\1\s*{\s*\1', re.IGNORECASE),  # Recursive nesting
            re.compile(r'first:\s*([5-9]\d{2,}|[1-9]\d{3,})', re.IGNORECASE),  # Large pagination
        ]
        return patterns
    
    async def on_request(self, info: GraphQLResolveInfo):
        """Security checks before query execution"""
        request = info.context.get("request")
        if not request:
            return
        
        # Get client information
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Check IP blocklist
        if ip_address in self.blocked_ips:
            await self._log_security_violation(
                "blocked_ip_access",
                SecurityThreatLevel.HIGH,
                None, ip_address,
                "Blocked IP attempted access"
            )
            raise GraphQLError("Access denied")
        
        # Rate limiting
        await self._check_rate_limits(info, ip_address)
        
        # Query analysis
        await self._analyze_query_security(info, ip_address)
        
        # Authentication validation
        await self._validate_authentication(info, ip_address)
    
    async def _check_rate_limits(self, info: GraphQLResolveInfo, ip_address: str):
        """Apply rate limiting based on operation type"""
        operation = info.operation
        operation_type = operation.operation.value if operation.operation else "query"
        
        # Different limits for different operations
        limits = {
            "query": {"calls": 100, "period": 60},
            "mutation": {"calls": 20, "period": 60},
            "subscription": {"calls": 5, "period": 60}
        }
        
        limit_config = limits.get(operation_type, limits["query"])
        
        # Apply rate limit
        if not await self.rate_limiter.check_limit(
            f"graphql:{operation_type}:{ip_address}",
            limit_config["calls"],
            limit_config["period"]
        ):
            await self._log_security_violation(
                "rate_limit_exceeded",
                SecurityThreatLevel.MEDIUM,
                None, ip_address,
                f"Rate limit exceeded for {operation_type}"
            )
            raise GraphQLError("Rate limit exceeded")
    
    async def _analyze_query_security(self, info: GraphQLResolveInfo, ip_address: str):
        """Analyze query for security threats"""
        query_string = str(info.context.get("query", ""))
        
        # Complexity analysis
        complexity_result = self.complexity_analyzer.analyze_query(info.schema.ast)
        if not complexity_result["is_valid"]:
            await self._log_security_violation(
                "query_complexity_violation",
                SecurityThreatLevel.HIGH,
                None, ip_address,
                f"Query complexity violation: {complexity_result['violations']}"
            )
            raise GraphQLError("Query too complex")
        
        # Pattern matching for suspicious queries
        for pattern in self.suspicious_patterns:
            if pattern.search(query_string):
                await self._log_security_violation(
                    "suspicious_query_pattern",
                    SecurityThreatLevel.MEDIUM,
                    None, ip_address,
                    f"Suspicious pattern detected: {pattern.pattern}"
                )
                
                # Block IP after multiple violations
                await self._increment_violation_count(ip_address)
                break
        
        # Check for introspection in production
        if settings.ENVIRONMENT == "production" and "__schema" in query_string:
            await self._log_security_violation(
                "introspection_in_production",
                SecurityThreatLevel.LOW,
                None, ip_address,
                "Introspection query in production"
            )
            # Don't block, just log
    
    async def _validate_authentication(self, info: GraphQLResolveInfo, ip_address: str):
        """Validate authentication tokens"""
        request = info.context.get("request")
        auth_header = request.headers.get("authorization", "")
        
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                # Validate JWT token
                payload = decode_jwt_token(token)
                
                # Check token expiration
                if payload.get("exp", 0) < time.time():
                    await self._log_security_violation(
                        "expired_token_usage",
                        SecurityThreatLevel.LOW,
                        payload.get("user_id"),
                        ip_address,
                        "Expired token used"
                    )
                    raise GraphQLError("Token expired")
                
                # Check for token anomalies
                await self._check_token_anomalies(payload, ip_address)
                
            except Exception as e:
                await self._log_security_violation(
                    "invalid_token",
                    SecurityThreatLevel.MEDIUM,
                    None, ip_address,
                    f"Invalid token: {str(e)}"
                )
                raise GraphQLError("Invalid authentication token")
    
    async def _check_token_anomalies(self, payload: Dict[str, Any], ip_address: str):
        """Check for token-based anomalies"""
        user_id = payload.get("user_id")
        
        # Check for unusual IP address for this user
        if user_id:
            recent_ips = await self._get_recent_user_ips(user_id)
            if ip_address not in recent_ips and len(recent_ips) > 0:
                await self._log_security_violation(
                    "unusual_ip_for_user",
                    SecurityThreatLevel.LOW,
                    user_id, ip_address,
                    "User accessing from unusual IP address"
                )
        
        # Check token age
        issued_at = payload.get("iat", 0)
        token_age = time.time() - issued_at
        if token_age > 86400 * 7:  # 7 days
            await self._log_security_violation(
                "old_token_usage",
                SecurityThreatLevel.LOW,
                user_id, ip_address,
                f"Old token used (age: {token_age/86400:.1f} days)"
            )
    
    async def resolve(self, next, root, info: GraphQLResolveInfo, **args):
        """Middleware resolver with field-level security"""
        # Pre-execution security checks
        await self.on_request(info)
        
        # Field-level authorization
        field_name = info.field_name
        await self._check_field_authorization(info, field_name)
        
        try:
            # Execute resolver
            result = await next(root, info, **args)
            
            # Post-execution security checks
            await self._check_response_security(info, result)
            
            return result
            
        except Exception as e:
            # Log resolver errors for security analysis
            await self._log_resolver_error(info, e)
            raise
    
    async def _check_field_authorization(self, info: GraphQLResolveInfo, field_name: str):
        """Check field-level authorization"""
        # Define sensitive fields that require special permissions
        sensitive_fields = {
            "email": "view_email",
            "phone": "view_phone",
            "private_data": "view_private_data",
            "analytics": "view_analytics",
            "revenue": "view_revenue",
            "payment_info": "view_payment_info"
        }
        
        if field_name in sensitive_fields:
            user = await get_current_user(info.context["request"])
            required_permission = sensitive_fields[field_name]
            
            if not user or not await verify_permissions(user, required_permission):
                ip_address = self._get_client_ip(info.context["request"])
                await self._log_security_violation(
                    "unauthorized_field_access",
                    SecurityThreatLevel.MEDIUM,
                    user.id if user else None,
                    ip_address,
                    f"Unauthorized access to field: {field_name}"
                )
                raise GraphQLError(f"Unauthorized access to field: {field_name}")
    
    async def _check_response_security(self, info: GraphQLResolveInfo, result: Any):
        """Check response for security issues"""
        # Check for data leakage in responses
        if isinstance(result, dict):
            # Remove sensitive fields from response if user lacks permissions
            user = await get_current_user(info.context["request"])
            if not user or not await verify_permissions(user, "admin"):
                sensitive_keys = ["password", "api_key", "secret", "private_key"]
                for key in sensitive_keys:
                    if key in result:
                        del result[key]
    
    async def _increment_violation_count(self, ip_address: str):
        """Increment violation count and block if threshold exceeded"""
        key = f"violations:{ip_address}"
        count = await self.rate_limiter.increment_counter(key, 3600)  # 1 hour TTL
        
        if count >= 5:  # Block after 5 violations
            self.blocked_ips.add(ip_address)
            await self._log_security_violation(
                "ip_blocked",
                SecurityThreatLevel.HIGH,
                None, ip_address,
                f"IP blocked after {count} violations"
            )
    
    def _get_client_ip(self, request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        return getattr(request.client, "host", "unknown")
    
    async def _get_recent_user_ips(self, user_id: str) -> List[str]:
        """Get recent IP addresses for user"""
        # This would typically query a user activity log
        # For this template, return empty list
        return []
    
    async def _log_security_violation(
        self,
        violation_type: str,
        threat_level: SecurityThreatLevel,
        user_id: Optional[str],
        ip_address: str,
        description: str
    ):
        """Log security violation"""
        violation = SecurityViolation(
            violation_type=violation_type,
            threat_level=threat_level,
            user_id=user_id,
            ip_address=ip_address,
            query=description,
            timestamp=datetime.utcnow(),
            metadata={
                "user_agent": "",  # Would extract from request
                "referrer": "",
                "session_id": ""
            }
        )
        
        # Log to security system
        log_security_event(
            event_type="graphql_security_violation",
            severity=threat_level.value,
            details=violation.__dict__
        )
        
        # Record metrics
        self.metrics.record_violation(violation_type, threat_level.value, user_id)
        
        # Alert on critical violations
        if threat_level == SecurityThreatLevel.CRITICAL:
            await self._send_security_alert(violation)
    
    async def _log_resolver_error(self, info: GraphQLResolveInfo, error: Exception):
        """Log resolver errors for security analysis"""
        logger.error(f"GraphQL resolver error in {info.field_name}: {str(error)}")
        
        # Track error patterns that might indicate attacks
        if any(keyword in str(error).lower() for keyword in ["sql", "injection", "union", "select"]):
            ip_address = self._get_client_ip(info.context["request"])
            await self._log_security_violation(
                "potential_injection_attempt",
                SecurityThreatLevel.HIGH,
                None, ip_address,
                f"Potential injection in {info.field_name}: {str(error)}"
            )
    
    async def _send_security_alert(self, violation: SecurityViolation):
        """Send alert for critical security violations"""
        # This would typically send alerts via email, Slack, etc.
        logger.critical(f"CRITICAL SECURITY VIOLATION: {violation.violation_type} from {violation.ip_address}")


class GraphQLInputSanitizer:
    """Sanitizes GraphQL inputs to prevent injection attacks"""
    
    def __init__(self):
        self.dangerous_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'on\w+\s*=', re.IGNORECASE),
            re.compile(r'union.*select.*from', re.IGNORECASE),
            re.compile(r'insert.*into.*values', re.IGNORECASE),
            re.compile(r'delete.*from.*where', re.IGNORECASE),
        ]
    
    def sanitize_input(self, value: Any) -> Any:
        """Sanitize input value"""
        if isinstance(value, str):
            return self._sanitize_string(value)
        elif isinstance(value, dict):
            return {k: self.sanitize_input(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.sanitize_input(item) for item in value]
        else:
            return value
    
    def _sanitize_string(self, value: str) -> str:
        """Sanitize string value"""
        # Remove dangerous patterns
        for pattern in self.dangerous_patterns:
            value = pattern.sub('', value)
        
        # HTML entity encoding for common XSS vectors
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')
        value = value.replace('"', '&quot;')
        value = value.replace("'", '&#x27;')
        
        return value.strip()


# Validation rules for GraphQL security
class NoIntrospectionRule(ValidationRule):
    """Validation rule to disable introspection in production"""
    
    def enter_field(self, node, *_):
        field_name = node.name.value
        if field_name in ["__schema", "__type"]:
            if settings.ENVIRONMENT == "production":
                self.report_error(
                    GraphQLError(
                        "Introspection is disabled in production",
                        nodes=[node]
                    )
                )


class DepthLimitRule(ValidationRule):
    """Validation rule to limit query depth"""
    
    def __init__(self, max_depth: int = 10):
        self.max_depth = max_depth
        self.current_depth = 0
    
    def enter_field(self, node, *_):
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.report_error(
                GraphQLError(
                    f"Query depth {self.current_depth} exceeds maximum {self.max_depth}",
                    nodes=[node]
                )
            )
    
    def leave_field(self, node, *_):
        self.current_depth -= 1


# Security middleware instance
graphql_security_middleware = GraphQLSecurityMiddleware()
input_sanitizer = GraphQLInputSanitizer()

# Security validation rules
SECURITY_VALIDATION_RULES = [
    NoIntrospectionRule,
    lambda: DepthLimitRule(max_depth=10)
]


# Export for template system
__all__ = [
    "GraphQLSecurityMiddleware",
    "QueryComplexityAnalyzer",
    "GraphQLInputSanitizer",
    "SecurityViolation",
    "SecurityThreatLevel",
    "NoIntrospectionRule",
    "DepthLimitRule",
    "graphql_security_middleware",
    "input_sanitizer",
    "SECURITY_VALIDATION_RULES"
]