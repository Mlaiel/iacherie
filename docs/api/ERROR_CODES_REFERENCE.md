# 🚨 Error Codes Reference - Ainflue API

## 🎯 Overview

This comprehensive reference covers all error codes, response formats, and troubleshooting guidance for the Ainflue API. Understanding these error codes will help you build robust applications with proper error handling.

## 📋 Error Response Format

All API errors follow a standardized format for consistency and ease of handling:

```json
{
  "error": {
    "code": "ERROR_CODE_HERE",
    "message": "Human-readable error description",
    "details": {
      "field": "specific_field_if_applicable",
      "value": "invalid_value_if_applicable",
      "constraints": ["validation rules that failed"]
    },
    "request_id": "req_uuid_for_tracking",
    "timestamp": "2025-01-07T10:00:00Z",
    "documentation_url": "https://docs.ainflue.com/errors/ERROR_CODE_HERE"
  }
}
```

### Error Response Headers
```http
Content-Type: application/json
X-Request-ID: req_12345
X-Error-Code: ERROR_CODE_HERE
X-Error-Category: VALIDATION_ERROR
```

## 🏗️ Error Categories

### 1. Client Errors (4xx)
Errors caused by invalid client requests

### 2. Server Errors (5xx)  
Errors caused by server-side issues

### 3. Authentication Errors (401)
Errors related to authentication and authorization

### 4. Rate Limiting Errors (429)
Errors related to rate limiting and quota exceeded

## 📊 HTTP Status Codes

| Status Code | Category | Description |
|-------------|----------|-------------|
| 400 | Bad Request | Invalid request syntax or parameters |
| 401 | Unauthorized | Authentication required or invalid |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 405 | Method Not Allowed | HTTP method not supported |
| 409 | Conflict | Resource conflict (duplicate, state mismatch) |
| 413 | Payload Too Large | Request payload exceeds size limits |
| 415 | Unsupported Media Type | Content-Type not supported |
| 422 | Unprocessable Entity | Valid syntax but semantic errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 502 | Bad Gateway | Upstream server error |
| 503 | Service Unavailable | Service temporarily unavailable |
| 504 | Gateway Timeout | Upstream server timeout |

## 🔐 Authentication Errors (401)

### AUTH_REQUIRED
```json
{
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "Authentication is required to access this resource",
    "details": {
      "supported_methods": ["Bearer JWT", "API Key"],
      "header_format": "Authorization: Bearer <token> or X-API-Key: <key>"
    }
  }
}
```

**Resolution**: Include valid authentication headers in your request.

### INVALID_TOKEN
```json
{
  "error": {
    "code": "INVALID_TOKEN",
    "message": "The provided authentication token is invalid",
    "details": {
      "token_type": "JWT",
      "reason": "Token signature verification failed"
    }
  }
}
```

**Resolution**: Obtain a new token through the login endpoint.

### TOKEN_EXPIRED
```json
{
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "The authentication token has expired",
    "details": {
      "expired_at": "2025-01-07T09:00:00Z",
      "refresh_endpoint": "/auth/refresh"
    }
  }
}
```

**Resolution**: Use the refresh token to obtain a new access token.

### INVALID_API_KEY
```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "The provided API key is invalid or revoked",
    "details": {
      "key_prefix": "ak_prod_",
      "dashboard_url": "https://dashboard.ainflue.com/api-keys"
    }
  }
}
```

**Resolution**: Verify your API key in the dashboard or generate a new one.

### INSUFFICIENT_SCOPE
```json
{
  "error": {
    "code": "INSUFFICIENT_SCOPE",
    "message": "The token does not have sufficient scope for this operation",
    "details": {
      "required_scopes": ["content:write", "ai:process"],
      "current_scopes": ["content:read"]
    }
  }
}
```

**Resolution**: Request a token with appropriate scopes or upgrade your account.

## 🚫 Authorization Errors (403)

### INSUFFICIENT_PERMISSIONS
```json
{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "You don't have permission to access this resource",
    "details": {
      "required_permission": "content:delete",
      "user_permissions": ["content:read", "content:write"],
      "resource_owner": "user_456"
    }
  }
}
```

**Resolution**: Request access from the resource owner or upgrade your permissions.

### ACCOUNT_SUSPENDED
```json
{
  "error": {
    "code": "ACCOUNT_SUSPENDED",
    "message": "Your account has been suspended",
    "details": {
      "reason": "Terms of service violation",
      "suspended_at": "2025-01-06T15:30:00Z",
      "appeal_url": "https://ainflue.com/appeals"
    }
  }
}
```

**Resolution**: Contact support to resolve the suspension.

### SUBSCRIPTION_REQUIRED
```json
{
  "error": {
    "code": "SUBSCRIPTION_REQUIRED",
    "message": "This feature requires a paid subscription",
    "details": {
      "feature": "Advanced AI Processing",
      "required_tier": "Pro",
      "current_tier": "Free",
      "upgrade_url": "https://ainflue.com/pricing"
    }
  }
}
```

**Resolution**: Upgrade your subscription to access this feature.

### FEATURE_DISABLED
```json
{
  "error": {
    "code": "FEATURE_DISABLED",
    "message": "This feature is disabled for your account",
    "details": {
      "feature": "Bulk Content Upload",
      "reason": "Enterprise feature",
      "contact_sales": "sales@ainflue.com"
    }
  }
}
```

**Resolution**: Contact sales to enable enterprise features.

## ✅ Validation Errors (400, 422)

### VALIDATION_ERROR
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid data",
    "details": {
      "field": "email",
      "value": "invalid-email",
      "constraints": ["must be a valid email address"]
    }
  }
}
```

**Resolution**: Fix the validation errors and resubmit the request.

### MISSING_REQUIRED_FIELD
```json
{
  "error": {
    "code": "MISSING_REQUIRED_FIELD",
    "message": "Required field is missing from the request",
    "details": {
      "field": "title",
      "location": "request_body",
      "example": "My Content Title"
    }
  }
}
```

**Resolution**: Include all required fields in your request.

### INVALID_FIELD_TYPE
```json
{
  "error": {
    "code": "INVALID_FIELD_TYPE",
    "message": "Field has incorrect data type",
    "details": {
      "field": "price",
      "expected_type": "number",
      "actual_type": "string",
      "provided_value": "not-a-number"
    }
  }
}
```

**Resolution**: Ensure field types match the API specification.

### FIELD_TOO_LONG
```json
{
  "error": {
    "code": "FIELD_TOO_LONG",
    "message": "Field value exceeds maximum length",
    "details": {
      "field": "description",
      "max_length": 1000,
      "actual_length": 1250,
      "truncated_value": "Content description that..."
    }
  }
}
```

**Resolution**: Reduce field length to meet requirements.

### INVALID_ENUM_VALUE
```json
{
  "error": {
    "code": "INVALID_ENUM_VALUE",
    "message": "Field value is not in allowed values",
    "details": {
      "field": "content_type",
      "provided_value": "document",
      "allowed_values": ["audio", "video", "image", "text"]
    }
  }
}
```

**Resolution**: Use one of the allowed enum values.

### INVALID_UUID_FORMAT
```json
{
  "error": {
    "code": "INVALID_UUID_FORMAT",
    "message": "Invalid UUID format provided",
    "details": {
      "field": "content_id",
      "provided_value": "not-a-uuid",
      "format": "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
    }
  }
}
```

**Resolution**: Provide a valid UUID v4 format.

### INVALID_DATE_FORMAT
```json
{
  "error": {
    "code": "INVALID_DATE_FORMAT",
    "message": "Invalid date format provided",
    "details": {
      "field": "start_date",
      "provided_value": "2025/01/07",
      "expected_format": "ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)"
    }
  }
}
```

**Resolution**: Use ISO 8601 date format.

## 🔍 Resource Errors (404, 409)

### RESOURCE_NOT_FOUND
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found",
    "details": {
      "resource_type": "content",
      "resource_id": "content_123",
      "possible_reasons": [
        "Resource was deleted",
        "Invalid ID provided",
        "Insufficient permissions"
      ]
    }
  }
}
```

**Resolution**: Verify the resource ID and your access permissions.

### RESOURCE_ALREADY_EXISTS
```json
{
  "error": {
    "code": "RESOURCE_ALREADY_EXISTS",
    "message": "A resource with this identifier already exists",
    "details": {
      "resource_type": "user",
      "conflicting_field": "email",
      "conflicting_value": "user@example.com",
      "existing_resource_id": "user_456"
    }
  }
}
```

**Resolution**: Use a different identifier or update the existing resource.

### RESOURCE_CONFLICT
```json
{
  "error": {
    "code": "RESOURCE_CONFLICT",
    "message": "The resource is in a state that conflicts with the request",
    "details": {
      "resource_type": "content",
      "resource_id": "content_123",
      "current_state": "processing",
      "required_state": "processed",
      "suggested_action": "Wait for processing to complete"
    }
  }
}
```

**Resolution**: Wait for the resource to reach the required state.

### DEPENDENCY_NOT_FOUND
```json
{
  "error": {
    "code": "DEPENDENCY_NOT_FOUND",
    "message": "A required dependency was not found",
    "details": {
      "dependency_type": "creator",
      "dependency_id": "creator_789",
      "dependent_resource": "content_123"
    }
  }
}
```

**Resolution**: Ensure all dependencies exist before creating the resource.

## 📁 Content-Specific Errors

### UNSUPPORTED_FILE_TYPE
```json
{
  "error": {
    "code": "UNSUPPORTED_FILE_TYPE",
    "message": "The uploaded file type is not supported",
    "details": {
      "file_name": "document.doc",
      "detected_type": "application/msword",
      "supported_types": [
        "audio/*", "video/*", "image/*", "text/plain"
      ]
    }
  }
}
```

**Resolution**: Convert the file to a supported format before uploading.

### FILE_SIZE_EXCEEDED
```json
{
  "error": {
    "code": "FILE_SIZE_EXCEEDED",
    "message": "The uploaded file exceeds the maximum size limit",
    "details": {
      "file_size": 157286400,
      "max_size": 104857600,
      "max_size_human": "100MB",
      "tier_limits": {
        "free": "10MB",
        "pro": "100MB",
        "enterprise": "1GB"
      }
    }
  }
}
```

**Resolution**: Reduce file size or upgrade your subscription tier.

### CORRUPTED_FILE
```json
{
  "error": {
    "code": "CORRUPTED_FILE",
    "message": "The uploaded file appears to be corrupted",
    "details": {
      "file_name": "audio.mp3",
      "corruption_indicators": [
        "Invalid header",
        "Unexpected EOF"
      ],
      "suggested_action": "Re-upload the file"
    }
  }
}
```

**Resolution**: Check the file integrity and re-upload.

### CONTENT_PROCESSING_FAILED
```json
{
  "error": {
    "code": "CONTENT_PROCESSING_FAILED",
    "message": "Content processing failed due to technical issues",
    "details": {
      "content_id": "content_123",
      "processing_stage": "ai_analysis",
      "failure_reason": "Insufficient audio quality",
      "retry_possible": true
    }
  }
}
```

**Resolution**: Try processing again or contact support for assistance.

### DUPLICATE_CONTENT_DETECTED
```json
{
  "error": {
    "code": "DUPLICATE_CONTENT_DETECTED",
    "message": "This content appears to be a duplicate of existing content",
    "details": {
      "similarity_score": 0.98,
      "existing_content_id": "content_456",
      "detection_method": "AI fingerprinting",
      "allow_duplicate": false
    }
  }
}
```

**Resolution**: Use the existing content or force upload with `allow_duplicate=true`.

## 🤖 AI Processing Errors

### AI_SERVICE_UNAVAILABLE
```json
{
  "error": {
    "code": "AI_SERVICE_UNAVAILABLE",
    "message": "AI processing service is temporarily unavailable",
    "details": {
      "service": "fingerprinting",
      "estimated_recovery": "2025-01-07T11:00:00Z",
      "alternative_endpoint": "/legacy/fingerprinting"
    }
  }
}
```

**Resolution**: Wait for service recovery or use alternative endpoint.

### AI_PROCESSING_TIMEOUT
```json
{
  "error": {
    "code": "AI_PROCESSING_TIMEOUT",
    "message": "AI processing operation timed out",
    "details": {
      "operation": "content_analysis",
      "timeout_duration": 300,
      "partial_results_available": true,
      "retry_with_lower_precision": true
    }
  }
}
```

**Resolution**: Retry with lower precision settings or reduce content complexity.

### INSUFFICIENT_AI_QUOTA
```json
{
  "error": {
    "code": "INSUFFICIENT_AI_QUOTA",
    "message": "AI processing quota exceeded for current billing period",
    "details": {
      "current_usage": 495,
      "quota_limit": 500,
      "quota_resets": "2025-02-01T00:00:00Z",
      "upgrade_options": ["Pro", "Enterprise"]
    }
  }
}
```

**Resolution**: Wait for quota reset or upgrade your subscription.

### AI_MODEL_ERROR
```json
{
  "error": {
    "code": "AI_MODEL_ERROR",
    "message": "AI model encountered an error during processing",
    "details": {
      "model": "fingerprint_v2",
      "error_type": "inference_failed",
      "fallback_model": "fingerprint_v1",
      "auto_fallback": true
    }
  }
}
```

**Resolution**: System will automatically retry with fallback model.

## 🚦 Rate Limiting Errors (429)

### RATE_LIMIT_EXCEEDED
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded for this endpoint",
    "details": {
      "limit": 1000,
      "window": "hour",
      "current_usage": 1000,
      "retry_after": 1800,
      "tier": "free",
      "upgrade_recommendation": "Pro tier offers 10x higher limits"
    }
  }
}
```

**Resolution**: Wait for the specified retry period or upgrade your tier.

### BURST_LIMIT_EXCEEDED
```json
{
  "error": {
    "code": "BURST_LIMIT_EXCEEDED",
    "message": "Burst rate limit exceeded",
    "details": {
      "burst_limit": 100,
      "window": "minute",
      "retry_after": 60,
      "suggestion": "Implement request pacing"
    }
  }
}
```

**Resolution**: Implement request pacing to stay within burst limits.

### CONCURRENT_REQUEST_LIMIT
```json
{
  "error": {
    "code": "CONCURRENT_REQUEST_LIMIT",
    "message": "Too many concurrent requests",
    "details": {
      "max_concurrent": 5,
      "current_concurrent": 7,
      "tier": "free",
      "retry_after": 30
    }
  }
}
```

**Resolution**: Reduce concurrent requests or upgrade your tier.

### QUOTA_EXCEEDED
```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Monthly quota exceeded",
    "details": {
      "quota_type": "api_requests",
      "quota_limit": 100000,
      "current_usage": 100000,
      "quota_resets": "2025-02-01T00:00:00Z"
    }
  }
}
```

**Resolution**: Wait for quota reset or purchase additional quota.

## 🔧 Server Errors (5xx)

### INTERNAL_SERVER_ERROR
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred on our servers",
    "details": {
      "error_id": "err_567890",
      "timestamp": "2025-01-07T10:15:30Z",
      "support_contact": "support@ainflue.com"
    }
  }
}
```

**Resolution**: Contact support with the error ID if the issue persists.

### SERVICE_UNAVAILABLE
```json
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Service is temporarily unavailable",
    "details": {
      "reason": "scheduled_maintenance",
      "estimated_recovery": "2025-01-07T12:00:00Z",
      "status_page": "https://status.ainflue.com"
    }
  }
}
```

**Resolution**: Check the status page and retry after the estimated recovery time.

### DATABASE_ERROR
```json
{
  "error": {
    "code": "DATABASE_ERROR",
    "message": "Database operation failed",
    "details": {
      "operation": "read",
      "table": "contents",
      "retry_possible": true,
      "error_id": "db_err_123"
    }
  }
}
```

**Resolution**: Retry the request. Contact support if the issue persists.

### UPSTREAM_SERVICE_ERROR
```json
{
  "error": {
    "code": "UPSTREAM_SERVICE_ERROR",
    "message": "Upstream service error",
    "details": {
      "service": "ai_processing",
      "upstream_status": 502,
      "retry_after": 120,
      "fallback_available": false
    }
  }
}
```

**Resolution**: Retry after the specified time.

## 🛠️ Error Handling Best Practices

### 1. Implement Proper Error Handling

```python
import requests
import time
from typing import Dict, Any

class AinflueFree:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.ainflue.com/v2"
    
    def handle_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request with comprehensive error handling."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                error_data = response.json().get('error', {})
                
                if error_data.get('code') == 'RATE_LIMIT_EXCEEDED':
                    print(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    return self.handle_request(method, endpoint, **kwargs)
            
            # Handle authentication errors
            elif response.status_code == 401:
                error_data = response.json().get('error', {})
                
                if error_data.get('code') == 'TOKEN_EXPIRED':
                    # Attempt to refresh token
                    self.refresh_token()
                    return self.handle_request(method, endpoint, **kwargs)
                
                raise AuthenticationError(error_data.get('message'))
            
            # Handle validation errors
            elif response.status_code == 400:
                error_data = response.json().get('error', {})
                raise ValidationError(error_data)
            
            # Handle server errors
            elif response.status_code >= 500:
                error_data = response.json().get('error', {})
                
                # Implement exponential backoff for server errors
                if error_data.get('code') in ['INTERNAL_SERVER_ERROR', 'SERVICE_UNAVAILABLE']:
                    return self.retry_with_backoff(method, endpoint, **kwargs)
                
                raise ServerError(error_data)
            
            # Success response
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {e}")
    
    def retry_with_backoff(self, method: str, endpoint: str, max_retries: int = 3, **kwargs):
        """Implement exponential backoff for server errors."""
        for attempt in range(max_retries):
            try:
                return self.handle_request(method, endpoint, **kwargs)
            except ServerError:
                if attempt == max_retries - 1:
                    raise
                
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)

# Custom exception classes
class AinflueFreeError(Exception):
    """Base exception for Ainflue API errors."""
    pass

class AuthenticationError(AinflueFreeError):
    """Authentication related errors."""
    pass

class ValidationError(AinflueFreeError):
    """Validation related errors."""
    pass

class ServerError(AinflueFreeError):
    """Server related errors."""
    pass

class NetworkError(AinflueFreeError):
    """Network related errors."""
    pass
```

### 2. Error Response Logging

```python
import logging
import json

def log_api_error(response):
    """Log API errors for debugging and monitoring."""
    if response.status_code >= 400:
        error_data = response.json().get('error', {})
        
        log_data = {
            'status_code': response.status_code,
            'error_code': error_data.get('code'),
            'error_message': error_data.get('message'),
            'request_id': error_data.get('request_id'),
            'timestamp': error_data.get('timestamp'),
            'endpoint': response.request.url,
            'method': response.request.method
        }
        
        # Log different levels based on error type
        if response.status_code >= 500:
            logging.error(f"Server Error: {json.dumps(log_data)}")
        elif response.status_code == 429:
            logging.warning(f"Rate Limited: {json.dumps(log_data)}")
        elif response.status_code >= 400:
            logging.info(f"Client Error: {json.dumps(log_data)}")
```

### 3. User-Friendly Error Messages

```python
def get_user_friendly_message(error_code: str, error_details: dict) -> str:
    """Convert technical error codes to user-friendly messages."""
    
    friendly_messages = {
        'AUTH_REQUIRED': "Please log in to access this feature.",
        'TOKEN_EXPIRED': "Your session has expired. Please log in again.",
        'VALIDATION_ERROR': f"Please check your input: {error_details.get('field', 'unknown field')} is invalid.",
        'RATE_LIMIT_EXCEEDED': "You're making requests too quickly. Please wait a moment and try again.",
        'FILE_SIZE_EXCEEDED': f"Your file is too large. Maximum size is {error_details.get('max_size_human', 'unknown')}.",
        'INSUFFICIENT_PERMISSIONS': "You don't have permission to perform this action.",
        'SUBSCRIPTION_REQUIRED': f"This feature requires a {error_details.get('required_tier', 'paid')} subscription.",
        'SERVICE_UNAVAILABLE': "The service is temporarily unavailable. Please try again later."
    }
    
    return friendly_messages.get(error_code, "An unexpected error occurred. Please try again.")
```

## 📊 Error Monitoring & Analytics

### Error Tracking Setup

```python
# Example using Sentry for error tracking
import sentry_sdk
from sentry_sdk.integrations.requests import RequestsIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[RequestsIntegration()],
    traces_sample_rate=1.0
)

def track_api_error(error_response):
    """Track API errors in monitoring system."""
    error_data = error_response.json().get('error', {})
    
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("api_error_code", error_data.get('code'))
        scope.set_tag("api_status_code", error_response.status_code)
        scope.set_extra("request_id", error_data.get('request_id'))
        scope.set_extra("error_details", error_data.get('details'))
        
        sentry_sdk.capture_message(
            f"Ainflue API Error: {error_data.get('message')}",
            level='error'
        )
```

### Error Rate Monitoring

```python
class ErrorRateMonitor:
    def __init__(self):
        self.error_counts = {}
        self.total_requests = 0
    
    def record_request(self, status_code: int, error_code: str = None):
        self.total_requests += 1
        
        if status_code >= 400:
            if error_code not in self.error_counts:
                self.error_counts[error_code] = 0
            self.error_counts[error_code] += 1
    
    def get_error_rate(self) -> float:
        total_errors = sum(self.error_counts.values())
        return (total_errors / self.total_requests) * 100 if self.total_requests > 0 else 0
    
    def get_top_errors(self, limit: int = 5) -> list:
        return sorted(
            self.error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
```

## 📞 Support & Troubleshooting

### When to Contact Support

1. **Persistent Server Errors (5xx)**
   - Include error ID and request ID
   - Describe your use case and expected behavior

2. **Unexpected Rate Limiting**
   - Provide usage patterns and timestamps
   - Include tier information and request volumes

3. **Authentication Issues**
   - Never share credentials or tokens
   - Provide error codes and timestamps

4. **Data Integrity Issues**
   - Provide request/response examples
   - Include content IDs and operation details

### Support Information

- **General Support**: support@ainflue.com
- **API Technical Support**: api-support@ainflue.com
- **Emergency Support**: +1-800-AINFLUE (Enterprise only)
- **Status Page**: https://status.ainflue.com
- **Documentation**: https://docs.ainflue.com

### Debug Information to Include

When contacting support, include:

```json
{
  "request_id": "req_12345",
  "timestamp": "2025-01-07T10:00:00Z",
  "endpoint": "POST /content/upload",
  "status_code": 500,
  "error_code": "INTERNAL_SERVER_ERROR",
  "api_version": "2.0",
  "sdk_version": "python-sdk-1.2.0",
  "account_tier": "pro"
}
```

---

## 📋 Quick Reference

### Most Common Errors

| Error Code | Status | Quick Fix |
|------------|--------|-----------|
| `AUTH_REQUIRED` | 401 | Add Authorization header |
| `TOKEN_EXPIRED` | 401 | Refresh your token |
| `VALIDATION_ERROR` | 400 | Check required fields |
| `RATE_LIMIT_EXCEEDED` | 429 | Wait and retry |
| `FILE_SIZE_EXCEEDED` | 413 | Reduce file size |
| `RESOURCE_NOT_FOUND` | 404 | Verify resource ID |
| `INSUFFICIENT_PERMISSIONS` | 403 | Check access rights |
| `SERVICE_UNAVAILABLE` | 503 | Check status page |

### Error Handling Checklist

- [ ] Implement proper exception handling
- [ ] Handle rate limiting with retries
- [ ] Log errors for debugging
- [ ] Provide user-friendly messages
- [ ] Monitor error rates
- [ ] Set up alerts for critical errors
- [ ] Document error handling in your code

---

**Last Updated**: January 7, 2025  
**Next Review**: April 2025  
**Version**: 2.0