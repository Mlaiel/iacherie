# API Management Guide - Enterprise Integration Security
=====================================================

## Table of Contents
- [Authentication & Authorization](#authentication--authorization)
- [Rate Limiting Strategies](#rate-limiting-strategies)
- [API Security Best Practices](#api-security-best-practices)
- [Error Handling & Monitoring](#error-handling--monitoring)
- [Data Encryption & Privacy](#data-encryption--privacy)
- [API Gateway Configuration](#api-gateway-configuration)
- [Performance Optimization](#performance-optimization)
- [Compliance & Auditing](#compliance--auditing)

## Authentication & Authorization

### OAuth 2.0 Implementation

#### Supported Grant Types
- **Authorization Code Grant**: For web applications
- **Client Credentials Grant**: For service-to-service communication
- **Device Code Grant**: For device authentication
- **PKCE Extension**: For mobile and single-page applications

```python
# OAuth Configuration Example
oauth_config = {
    "authorization_endpoint": "https://api.ainflue.com/oauth/authorize",
    "token_endpoint": "https://api.ainflue.com/oauth/token",
    "revocation_endpoint": "https://api.ainflue.com/oauth/revoke",
    "scopes": {
        "read": "Read access to content and analytics",
        "write": "Create and modify content",
        "admin": "Administrative access",
        "payment": "Access to payment operations",
        "monetization": "Creator monetization features"
    },
    "token_lifetime": 3600,  # 1 hour
    "refresh_token_lifetime": 604800,  # 7 days
    "pkce_required": True
}
```

#### API Key Management

```python
# API Key Configuration
api_key_config = {
    "key_formats": {
        "development": "dev_[32_chars]",
        "production": "prod_[32_chars]",
        "restricted": "rest_[32_chars]"
    },
    "rate_limits": {
        "development": 1000,  # requests per hour
        "production": 10000,
        "restricted": 100
    },
    "auto_rotation": True,
    "rotation_interval": 2592000,  # 30 days
    "notification_before_expiry": 604800  # 7 days
}
```

### Multi-Factor Authentication (MFA)

#### TOTP Implementation
```python
import pyotp
import qrcode

def setup_mfa_for_api_access(user_id: str) -> dict:
    """Setup MFA for API access."""
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    
    qr_url = totp.provisioning_uri(
        name=user_id,
        issuer_name="Ainflue API"
    )
    
    return {
        "secret": secret,
        "qr_code_url": qr_url,
        "backup_codes": generate_backup_codes(),
        "current_token": totp.now()
    }
```

## Rate Limiting Strategies

### Adaptive Rate Limiting

```python
class AdaptiveRateLimit:
    """Intelligent rate limiting based on usage patterns."""
    
    def __init__(self):
        self.base_limits = {
            "free": {"requests": 1000, "window": 3600},
            "pro": {"requests": 10000, "window": 3600},
            "enterprise": {"requests": 100000, "window": 3600}
        }
        self.burst_allowance = 1.5
        self.penalty_factor = 0.5
    
    async def check_rate_limit(self, api_key: str, endpoint: str) -> dict:
        """Check if request is within rate limits."""
        usage = await self.get_usage_stats(api_key)
        tier = await self.get_api_tier(api_key)
        
        base_limit = self.base_limits[tier]["requests"]
        time_window = self.base_limits[tier]["window"]
        
        # Adaptive adjustments
        if usage["error_rate"] < 0.01:  # Low error rate
            adjusted_limit = int(base_limit * self.burst_allowance)
        elif usage["error_rate"] > 0.1:  # High error rate
            adjusted_limit = int(base_limit * self.penalty_factor)
        else:
            adjusted_limit = base_limit
        
        current_usage = await self.get_current_usage(api_key, time_window)
        
        return {
            "allowed": current_usage < adjusted_limit,
            "remaining": max(0, adjusted_limit - current_usage),
            "reset_time": self.get_reset_time(time_window),
            "limit": adjusted_limit
        }
```

### Rate Limiting by Endpoint Category

```python
ENDPOINT_CATEGORIES = {
    "analytics": {"weight": 1, "burst": True},
    "content_upload": {"weight": 10, "burst": False},
    "payment": {"weight": 5, "burst": False},
    "social_media": {"weight": 2, "burst": True},
    "ai_processing": {"weight": 20, "burst": False}
}
```

## API Security Best Practices

### Request Validation & Sanitization

```python
from marshmallow import Schema, fields, validate
from typing import Dict, Any

class PaymentRequestSchema(Schema):
    """Validation schema for payment requests."""
    amount = fields.Decimal(required=True, validate=validate.Range(min=0.01, max=10000))
    currency = fields.Str(required=True, validate=validate.OneOf(['USD', 'EUR', 'GBP']))
    creator_id = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    description = fields.Str(validate=validate.Length(max=500))
    metadata = fields.Dict(keys=fields.Str(), values=fields.Raw())

def validate_request(schema: Schema, data: Dict[str, Any]) -> tuple:
    """Validate incoming request data."""
    try:
        result = schema.load(data)
        return True, result, None
    except ValidationError as e:
        return False, None, e.messages
```

### SQL Injection Prevention

```python
# Safe database queries using parameterized statements
async def get_creator_analytics(creator_id: str, start_date: datetime, end_date: datetime):
    """Safely retrieve creator analytics."""
    query = """
    SELECT metric_name, metric_value, recorded_at
    FROM creator_analytics 
    WHERE creator_id = $1 
    AND recorded_at BETWEEN $2 AND $3
    ORDER BY recorded_at DESC
    """
    
    # Using parameterized query prevents SQL injection
    return await database.fetch_all(query, creator_id, start_date, end_date)
```

### XSS Prevention

```python
import bleach
from markupsafe import escape

def sanitize_user_content(content: str) -> str:
    """Sanitize user-generated content."""
    # Allow only safe HTML tags
    allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
    allowed_attributes = {}
    
    # Clean HTML
    clean_content = bleach.clean(
        content, 
        tags=allowed_tags, 
        attributes=allowed_attributes,
        strip=True
    )
    
    # Additional escaping for extra safety
    return escape(clean_content)
```

## Error Handling & Monitoring

### Structured Error Responses

```python
from enum import Enum
from typing import Optional, List, Dict, Any

class ErrorCode(Enum):
    """Standardized error codes."""
    INVALID_API_KEY = "E001"
    RATE_LIMIT_EXCEEDED = "E002"
    INSUFFICIENT_PERMISSIONS = "E003"
    RESOURCE_NOT_FOUND = "E004"
    VALIDATION_ERROR = "E005"
    PAYMENT_FAILED = "E006"
    SERVICE_UNAVAILABLE = "E007"

class APIError:
    """Structured API error response."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.request_id = request_id
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response."""
        return {
            "error": {
                "code": self.code.value,
                "message": self.message,
                "details": self.details,
                "request_id": self.request_id,
                "timestamp": self.timestamp,
                "documentation_url": f"https://docs.ainflue.com/errors/{self.code.value}"
            }
        }
```

### Request Logging & Monitoring

```python
import structlog
from typing import Dict, Any

logger = structlog.get_logger()

async def log_api_request(
    request_id: str,
    api_key: str,
    endpoint: str,
    method: str,
    ip_address: str,
    user_agent: str,
    payload_size: int,
    response_status: int,
    response_time_ms: float
):
    """Log API request for monitoring and auditing."""
    
    log_data = {
        "request_id": request_id,
        "api_key_hash": hashlib.sha256(api_key.encode()).hexdigest()[:16],
        "endpoint": endpoint,
        "method": method,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "payload_size": payload_size,
        "response_status": response_status,
        "response_time_ms": response_time_ms,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Log to structured logging system
    if response_status >= 400:
        logger.warning("API request failed", **log_data)
    elif response_time_ms > 1000:
        logger.warning("Slow API request", **log_data)
    else:
        logger.info("API request completed", **log_data)
    
    # Send to monitoring system
    await send_to_monitoring_system(log_data)
```

## Data Encryption & Privacy

### Encryption at Rest

```python
from cryptography.fernet import Fernet
import os

class DataEncryption:
    """Handle data encryption for sensitive information."""
    
    def __init__(self):
        # Use environment variable for encryption key
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
            # Store securely in production
        
        self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data before storage."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data after retrieval."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

### PII Data Handling

```python
import re
from typing import Dict, Any, List

class PIIDetector:
    """Detect and handle Personally Identifiable Information."""
    
    def __init__(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }
    
    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII in text content."""
        detected = []
        
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                detected.append({
                    'type': pii_type,
                    'value': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
        
        return detected
    
    def redact_pii(self, text: str) -> str:
        """Redact PII from text content."""
        for pii_type, pattern in self.patterns.items():
            text = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', text)
        
        return text
```

## API Gateway Configuration

### Load Balancing Configuration

```yaml
# API Gateway Load Balancer Configuration
load_balancer:
  algorithm: "weighted_round_robin"
  health_checks:
    interval: 30s
    timeout: 5s
    healthy_threshold: 2
    unhealthy_threshold: 3
  
  upstream_servers:
    - server: "api-server-1.internal:8080"
      weight: 100
      max_conns: 1000
    - server: "api-server-2.internal:8080"
      weight: 100
      max_conns: 1000
    - server: "api-server-3.internal:8080"
      weight: 50  # Smaller instance
      max_conns: 500

  circuit_breaker:
    failure_threshold: 5
    recovery_timeout: 30s
    half_open_max_calls: 3
```

### Caching Strategy

```python
from typing import Optional, Any
import redis
import json

class APICache:
    """API response caching for performance optimization."""
    
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.default_ttl = 300  # 5 minutes
        
        # Cache TTL by endpoint category
        self.cache_config = {
            "analytics": 3600,      # 1 hour
            "content_metadata": 1800,  # 30 minutes
            "creator_profile": 600,    # 10 minutes
            "real_time_data": 60      # 1 minute
        }
    
    async def get_cached_response(
        self, 
        cache_key: str, 
        category: str = "default"
    ) -> Optional[Any]:
        """Retrieve cached API response."""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None
    
    async def cache_response(
        self, 
        cache_key: str, 
        data: Any, 
        category: str = "default"
    ):
        """Cache API response with appropriate TTL."""
        try:
            ttl = self.cache_config.get(category, self.default_ttl)
            self.redis_client.setex(
                cache_key, 
                ttl, 
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
```

## Performance Optimization

### Connection Pooling

```python
import asyncpg
import aioredis
from contextlib import asynccontextmanager

class ConnectionManager:
    """Manage database and cache connections efficiently."""
    
    def __init__(self):
        self.db_pool = None
        self.redis_pool = None
    
    async def initialize(self):
        """Initialize connection pools."""
        # PostgreSQL connection pool
        self.db_pool = await asyncpg.create_pool(
            host="localhost",
            database="ainflue",
            user="api_user",
            password=os.environ.get("DB_PASSWORD"),
            min_size=10,
            max_size=20,
            command_timeout=60
        )
        
        # Redis connection pool
        self.redis_pool = aioredis.ConnectionPool.from_url(
            "redis://localhost:6379",
            max_connections=20
        )
    
    @asynccontextmanager
    async def get_db_connection(self):
        """Get database connection from pool."""
        async with self.db_pool.acquire() as connection:
            yield connection
    
    @asynccontextmanager
    async def get_redis_connection(self):
        """Get Redis connection from pool."""
        redis = aioredis.Redis(connection_pool=self.redis_pool)
        try:
            yield redis
        finally:
            await redis.close()
```

### Async Request Processing

```python
import asyncio
from typing import List, Dict, Any
import aiohttp

class BatchProcessor:
    """Process multiple API requests efficiently."""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_batch_requests(
        self, 
        requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process multiple requests concurrently."""
        async def process_single_request(request_data):
            async with self.semaphore:
                return await self.process_request(request_data)
        
        # Execute all requests concurrently
        tasks = [process_single_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "request_id": requests[i].get("id")
                })
            else:
                processed_results.append(result)
        
        return processed_results
```

## Compliance & Auditing

### GDPR Compliance

```python
class GDPRCompliance:
    """Handle GDPR compliance requirements."""
    
    async def handle_data_subject_request(
        self, 
        request_type: str, 
        user_id: str
    ) -> Dict[str, Any]:
        """Handle GDPR data subject requests."""
        
        if request_type == "access":
            return await self.export_user_data(user_id)
        elif request_type == "deletion":
            return await self.delete_user_data(user_id)
        elif request_type == "portability":
            return await self.export_portable_data(user_id)
        elif request_type == "rectification":
            return await self.update_user_data(user_id)
    
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for GDPR access request."""
        user_data = {
            "personal_info": await self.get_personal_info(user_id),
            "content_data": await self.get_content_data(user_id),
            "analytics_data": await self.get_analytics_data(user_id),
            "payment_data": await self.get_payment_data(user_id),
            "interaction_data": await self.get_interaction_data(user_id)
        }
        
        # Log the data export
        await self.log_gdpr_action("data_export", user_id)
        
        return user_data
```

### Audit Logging

```python
class AuditLogger:
    """Comprehensive audit logging for compliance."""
    
    async def log_sensitive_operation(
        self,
        operation: str,
        user_id: str,
        resource_id: str,
        before_state: Optional[Dict] = None,
        after_state: Optional[Dict] = None,
        ip_address: Optional[str] = None
    ):
        """Log sensitive operations for audit trail."""
        
        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "user_id": user_id,
            "resource_id": resource_id,
            "before_state": before_state,
            "after_state": after_state,
            "ip_address": ip_address,
            "api_version": "v1.0",
            "success": True
        }
        
        # Store in audit database
        await self.store_audit_entry(audit_entry)
        
        # Send to SIEM system if configured
        await self.send_to_siem(audit_entry)
```

---

## Security Contacts

**Security Team**: security@ainflue.com  
**Bug Bounty Program**: [https://bugcrowd.com/ainflue](https://bugcrowd.com/ainflue)  
**Emergency Contact**: +1-555-SECURITY  

## Legal Notice

This API management guide contains confidential and proprietary information of Ainflue. Unauthorized access, use, or distribution is prohibited and may result in legal action.

**© 2025 Fahed Mlaiel. All rights reserved.**

## Enterprise API Management for Ainflue Integrations

**Author:** Fahed Mlaiel <mlaiel@live.de>  
**Copyright:** (c) 2025 Fahed Mlaiel. All rights reserved.

---

## Overview

This guide provides comprehensive best practices for managing APIs across 100+ third-party integrations in the Ainflue platform, ensuring high performance, reliability, and security.

## API Gateway Design Principles

### 1. Single Entry Point
- All external API calls route through the API Gateway
- Centralized request/response handling
- Unified logging and monitoring
- Consistent error handling

### 2. Service Abstraction
- Hide backend complexity from clients
- Protocol translation (REST ↔ GraphQL ↔ gRPC)
- Versioning management
- Backward compatibility

### 3. Cross-Cutting Concerns
- Authentication and authorization
- Rate limiting and throttling
- Request/response transformation
- Caching and compression

## Request Lifecycle Management

### Request Processing Pipeline

```python
async def process_request(self, request: APIRequest) -> APIResponse:
    """Complete request processing pipeline."""
    
    # 1. Request Validation
    if not await self._validate_request(request):
        return self._create_error_response(400, "Invalid request")
    
    # 2. Authentication Check
    auth_result = await self.auth_handler.authenticate_request(request)
    if not auth_result.success:
        return self._create_error_response(401, "Authentication failed")
    
    # 3. Rate Limiting
    if not await self.rate_limiter.can_proceed(request.integration_name):
        return self._create_error_response(429, "Rate limit exceeded")
    
    # 4. Circuit Breaker Check
    if not await self.circuit_breaker.is_available(request.integration_name):
        return self._create_error_response(503, "Service unavailable")
    
    # 5. Cache Check
    cached_response = await self.cache_manager.get_cached_response(
        request.integration_name, request.endpoint, request.params
    )
    if cached_response:
        return self._create_cached_response(cached_response)
    
    # 6. Load Balancing
    endpoint = await self._select_endpoint(request.integration_name)
    if not endpoint:
        return self._create_error_response(503, "No healthy endpoints")
    
    # 7. Request Transformation
    transformed_request = await self._transform_request(request)
    
    # 8. Execute Request
    response = await self._execute_request(transformed_request, endpoint)
    
    # 9. Response Transformation
    transformed_response = await self._transform_response(response)
    
    # 10. Cache Response
    await self.cache_manager.cache_response(
        request.integration_name, request.endpoint, transformed_response
    )
    
    # 11. Metrics and Logging
    await self._record_metrics(request, response)
    
    return transformed_response
```

## Load Balancing Strategies

### 1. Health-Based Routing

```python
def _select_healthiest_endpoint(self, endpoints: List[APIEndpoint]) -> APIEndpoint:
    """Select endpoint based on health score."""
    
    def calculate_health_score(endpoint: APIEndpoint) -> float:
        # Success rate (40% weight)
        success_rate = 1.0 - (endpoint.failed_requests / max(endpoint.total_requests, 1))
        
        # Connection load (30% weight)
        connection_load = 1.0 - (endpoint.current_connections / max(endpoint.max_connections, 1))
        
        # Response time (30% weight)
        response_factor = 1.0 / (1.0 + endpoint.average_response_time)
        
        return (success_rate * 0.4 + connection_load * 0.3 + response_factor * 0.3) * endpoint.weight
    
    return max(endpoints, key=calculate_health_score)
```

### 2. Weighted Round Robin

```python
def _select_weighted_round_robin(self, endpoints: List[APIEndpoint]) -> APIEndpoint:
    """Weighted round-robin with dynamic weight adjustment."""
    
    total_weight = sum(endpoint.weight for endpoint in endpoints)
    current_position = self.round_robin_state[integration_name]
    
    # Adjust weights based on performance
    for endpoint in endpoints:
        if endpoint.average_response_time > 2.0:  # Slow endpoint
            endpoint.weight = max(1, endpoint.weight * 0.8)
        elif endpoint.average_response_time < 0.5:  # Fast endpoint
            endpoint.weight = min(10, endpoint.weight * 1.2)
    
    # Select based on weighted position
    accumulated_weight = 0
    for endpoint in endpoints:
        accumulated_weight += endpoint.weight
        if current_position <= accumulated_weight:
            self.round_robin_state[integration_name] = (current_position + 1) % total_weight
            return endpoint
    
    return endpoints[0]  # Fallback
```

## Rate Limiting Implementation

### 1. Token Bucket Algorithm

```python
class TokenBucket:
    """Token bucket rate limiter implementation."""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Consume tokens from bucket."""
        now = time.time()
        
        # Add tokens based on time elapsed
        time_passed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + time_passed * self.refill_rate
        )
        self.last_refill = now
        
        # Check if enough tokens available
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """Calculate wait time for required tokens."""
        if self.tokens >= tokens:
            return 0.0
        
        needed_tokens = tokens - self.tokens
        return needed_tokens / self.refill_rate
```

### 2. Sliding Window Rate Limiter

```python
class SlidingWindowRateLimiter:
    """Sliding window rate limiter with Redis backend."""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
    
    async def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is allowed within sliding window."""
        
        now = time.time()
        window_start = now - window_seconds
        
        # Redis Lua script for atomic operation
        lua_script = """
        local key = KEYS[1]
        local window_start = tonumber(ARGV[1])
        local now = tonumber(ARGV[2])
        local limit = tonumber(ARGV[3])
        
        -- Remove old entries
        redis.call('ZREMRANGEBYSCORE', key, 0, window_start)
        
        -- Count current requests
        local current_count = redis.call('ZCARD', key)
        
        if current_count < limit then
            -- Add current request
            redis.call('ZADD', key, now, now)
            redis.call('EXPIRE', key, ARGV[4])
            return {1, current_count + 1, limit - current_count - 1}
        else
            return {0, current_count, 0}
        end
        """
        
        result = await self.redis.eval(
            lua_script,
            keys=[key],
            args=[window_start, now, limit, window_seconds]
        )
        
        allowed = bool(result[0])
        current_count = result[1]
        remaining = result[2]
        
        return allowed, {
            "allowed": allowed,
            "current_count": current_count,
            "remaining": remaining,
            "reset_time": now + window_seconds
        }
```

## Caching Strategies

### 1. Multi-Level Cache Implementation

```python
class MultiLevelCache:
    """Multi-level caching with L1 (memory), L2 (Redis), L3 (disk)."""
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value with cache hierarchy."""
        
        # L1 Cache (Memory) - Fastest
        value = await self._get_from_memory(key)
        if value is not None:
            await self._promote_to_memory(key, value)
            return value
        
        # L2 Cache (Redis) - Fast, distributed
        value = await self._get_from_redis(key)
        if value is not None:
            await self._store_in_memory(key, value)
            return value
        
        # L3 Cache (Disk) - Slower but persistent
        value = await self._get_from_disk(key)
        if value is not None:
            await self._store_in_redis(key, value)
            await self._store_in_memory(key, value)
            return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in all cache levels."""
        success = True
        
        # Store in all levels
        success &= await self._store_in_memory(key, value, ttl)
        success &= await self._store_in_redis(key, value, ttl)
        success &= await self._store_in_disk(key, value, ttl)
        
        return success
```

### 2. Cache Invalidation Patterns

```python
class CacheInvalidationManager:
    """Manages cache invalidation across all levels."""
    
    async def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern."""
        invalidated_count = 0
        
        # Invalidate memory cache
        memory_keys = [key for key in self.memory_cache.keys() if self._matches_pattern(key, pattern)]
        for key in memory_keys:
            del self.memory_cache[key]
            invalidated_count += 1
        
        # Invalidate Redis cache
        if self.redis_client:
            async for key in self.redis_client.scan_iter(match=pattern):
                await self.redis_client.delete(key)
                invalidated_count += 1
        
        # Invalidate disk cache
        invalidated_count += await self._invalidate_disk_pattern(pattern)
        
        return invalidated_count
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags."""
        invalidated_count = 0
        
        for tag in tags:
            # Get keys associated with tag
            tagged_keys = await self._get_keys_by_tag(tag)
            
            for key in tagged_keys:
                await self.delete(key)
                invalidated_count += 1
        
        return invalidated_count
```

## Request/Response Transformation

### 1. Data Transformation Pipeline

```python
class TransformationEngine:
    """Handles request/response data transformations."""
    
    def __init__(self):
        self.transformers = {}
        self.schemas = {}
    
    async def transform_request(
        self,
        integration_name: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform request data for specific integration."""
        
        transformer = self.transformers.get(integration_name)
        if not transformer:
            return data
        
        # Apply transformation rules
        transformed_data = {}
        
        for source_field, target_field in transformer.field_mappings.items():
            if source_field in data:
                transformed_data[target_field] = await self._transform_field_value(
                    data[source_field],
                    transformer.field_transformations.get(source_field)
                )
        
        # Apply custom transformation functions
        if transformer.custom_transform:
            transformed_data = await transformer.custom_transform(transformed_data)
        
        # Validate against schema
        if integration_name in self.schemas:
            await self._validate_schema(transformed_data, self.schemas[integration_name])
        
        return transformed_data
    
    async def _transform_field_value(self, value: Any, transformation: Optional[str]) -> Any:
        """Apply field-level transformations."""
        if not transformation:
            return value
        
        transformations = {
            "uppercase": lambda x: str(x).upper(),
            "lowercase": lambda x: str(x).lower(),
            "timestamp_to_iso": lambda x: datetime.fromtimestamp(x).isoformat(),
            "base64_encode": lambda x: base64.b64encode(str(x).encode()).decode(),
            "url_encode": lambda x: urllib.parse.quote(str(x))
        }
        
        transform_func = transformations.get(transformation)
        return transform_func(value) if transform_func else value
```

### 2. Response Normalization

```python
class ResponseNormalizer:
    """Normalize responses from different providers to common format."""
    
    async def normalize_response(
        self,
        integration_name: str,
        raw_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize provider response to standard format."""
        
        normalizers = {
            "youtube": self._normalize_youtube_response,
            "instagram": self._normalize_instagram_response,
            "tiktok": self._normalize_tiktok_response,
            "spotify": self._normalize_spotify_response
        }
        
        normalizer = normalizers.get(integration_name, self._default_normalizer)
        return await normalizer(raw_response)
    
    async def _normalize_youtube_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize YouTube API response."""
        return {
            "id": response.get("id"),
            "title": response.get("snippet", {}).get("title"),
            "description": response.get("snippet", {}).get("description"),
            "thumbnail": response.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url"),
            "published_at": response.get("snippet", {}).get("publishedAt"),
            "view_count": response.get("statistics", {}).get("viewCount"),
            "like_count": response.get("statistics", {}).get("likeCount"),
            "provider": "youtube",
            "raw_data": response
        }
    
    async def _normalize_instagram_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Instagram API response."""
        return {
            "id": response.get("id"),
            "title": response.get("caption", ""),
            "description": response.get("caption", ""),
            "thumbnail": response.get("media_url"),
            "published_at": response.get("timestamp"),
            "like_count": response.get("like_count"),
            "comment_count": response.get("comments_count"),
            "provider": "instagram",
            "raw_data": response
        }
```

## Error Handling and Resilience

### 1. Circuit Breaker Pattern

```python
class APICircuitBreaker:
    """Circuit breaker for API endpoints."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        
        except Exception as e:
            await self._on_failure()
            raise e
    
    async def _on_success(self):
        """Handle successful request."""
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
    
    async def _on_failure(self):
        """Handle failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset."""
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
```

### 2. Retry Logic with Exponential Backoff

```python
class ExponentialBackoffRetry:
    """Retry logic with exponential backoff and jitter."""
    
    async def retry_with_backoff(
        self,
        func: Callable,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retry_on: List[Type[Exception]] = None
    ) -> Any:
        """Execute function with exponential backoff retry."""
        
        retry_on = retry_on or [requests.RequestException, httpx.HTTPError]
        
        for attempt in range(max_attempts):
            try:
                return await func()
            
            except Exception as e:
                if attempt == max_attempts - 1:  # Last attempt
                    raise e
                
                if not any(isinstance(e, exc_type) for exc_type in retry_on):
                    raise e  # Don't retry non-retryable exceptions
                
                # Calculate delay
                delay = min(base_delay * (exponential_base ** attempt), max_delay)
                
                if jitter:
                    delay = delay * (0.5 + random.random() * 0.5)  # Add jitter
                
                await asyncio.sleep(delay)
        
        raise Exception(f"Max retry attempts ({max_attempts}) exceeded")
```

## Monitoring and Observability

### 1. Request Metrics Collection

```python
class APIMetricsCollector:
    """Collect and aggregate API metrics."""
    
    async def record_request(
        self,
        integration_name: str,
        endpoint: str,
        method: str,
        response_time: float,
        status_code: int,
        request_size: int,
        response_size: int
    ):
        """Record API request metrics."""
        
        # Response time histogram
        await self.metrics.histogram(
            "api.request.duration",
            response_time,
            tags={
                "integration": integration_name,
                "endpoint": endpoint,
                "method": method,
                "status_code": str(status_code)
            }
        )
        
        # Request count
        await self.metrics.increment(
            "api.request.count",
            tags={
                "integration": integration_name,
                "endpoint": endpoint,
                "method": method,
                "status_code": str(status_code)
            }
        )
        
        # Request/response size
        await self.metrics.histogram("api.request.size", request_size)
        await self.metrics.histogram("api.response.size", response_size)
        
        # Error rate calculation
        if status_code >= 400:
            await self.metrics.increment(
                "api.request.errors",
                tags={"integration": integration_name, "status_code": str(status_code)}
            )
```

### 2. Health Check Implementation

```python
class APIHealthChecker:
    """Monitor API endpoint health."""
    
    async def check_endpoint_health(self, endpoint: APIEndpoint) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        
        start_time = time.time()
        health_result = {
            "endpoint": endpoint.name,
            "url": endpoint.base_url,
            "healthy": False,
            "response_time": 0.0,
            "status_code": None,
            "error": None,
            "checked_at": datetime.utcnow().isoformat()
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{endpoint.base_url}/health")
                
                health_result["status_code"] = response.status_code
                health_result["response_time"] = time.time() - start_time
                health_result["healthy"] = 200 <= response.status_code < 300
                
                # Additional health checks
                if response.status_code == 200:
                    health_data = response.json()
                    health_result["details"] = health_data
                
        except Exception as e:
            health_result["error"] = str(e)
            health_result["response_time"] = time.time() - start_time
        
        return health_result
```

## Security Best Practices

### 1. API Key Management

```python
class APIKeyManager:
    """Secure API key management."""
    
    def __init__(self, encryption_key: bytes):
        self.cipher_suite = Fernet(encryption_key)
        self.key_rotation_interval = 86400  # 24 hours
    
    async def store_api_key(
        self,
        integration_name: str,
        api_key: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Store API key securely."""
        
        # Encrypt API key
        encrypted_key = self.cipher_suite.encrypt(api_key.encode())
        
        # Generate key ID
        key_id = secrets.token_hex(16)
        
        # Store in secure storage
        await self.secure_storage.store({
            "key_id": key_id,
            "integration_name": integration_name,
            "encrypted_key": encrypted_key.decode(),
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        })
        
        return key_id
    
    async def retrieve_api_key(self, key_id: str) -> Optional[str]:
        """Retrieve and decrypt API key."""
        
        key_data = await self.secure_storage.get(key_id)
        if not key_data:
            return None
        
        # Decrypt API key
        encrypted_key = key_data["encrypted_key"].encode()
        api_key = self.cipher_suite.decrypt(encrypted_key).decode()
        
        return api_key
```

### 2. Request Signing

```python
class RequestSigner:
    """Sign API requests for security."""
    
    def __init__(self, signing_key: str):
        self.signing_key = signing_key.encode()
    
    def sign_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Optional[str] = None,
        timestamp: Optional[int] = None
    ) -> str:
        """Generate request signature."""
        
        timestamp = timestamp or int(time.time())
        
        # Create string to sign
        string_to_sign = f"{method}\n{url}\n{timestamp}"
        
        if body:
            body_hash = hashlib.sha256(body.encode()).hexdigest()
            string_to_sign += f"\n{body_hash}"
        
        # Generate signature
        signature = hmac.new(
            self.signing_key,
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}.{signature}"
    
    def verify_signature(
        self,
        signature: str,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Optional[str] = None,
        max_age: int = 300  # 5 minutes
    ) -> bool:
        """Verify request signature."""
        
        try:
            timestamp_str, received_signature = signature.split(".", 1)
            timestamp = int(timestamp_str)
            
            # Check timestamp freshness
            if abs(time.time() - timestamp) > max_age:
                return False
            
            # Generate expected signature
            expected_signature = self.sign_request(method, url, headers, body, timestamp)
            expected_sig_part = expected_signature.split(".", 1)[1]
            
            # Constant-time comparison
            return hmac.compare_digest(received_signature, expected_sig_part)
            
        except (ValueError, IndexError):
            return False
```

---

**Performance Note:** All API management patterns should be implemented with async/await for optimal performance in high-throughput scenarios.

**Security Note:** Always validate input, use HTTPS, implement proper authentication, and log security events for audit purposes.

**Contact:** mlaiel@live.de for API management consultation and support.