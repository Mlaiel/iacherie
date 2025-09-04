# 🚀 Ainflue Public API Documentation

## Overview

The Ainflue Public API provides developer-friendly access to our AI-powered content protection and monetization platform. This API is specifically designed for:

- **SDK Integration**: Seamless integration with our official SDKs
- **Developer Tools**: Testing sandbox and development utilities  
- **Content Analysis**: AI-powered content fingerprinting and analysis
- **Documentation**: Interactive API documentation and examples

## 🔗 Base URL

```
Production: https://api.ainflue.com/api/v1/public
Staging: https://staging-api.ainflue.com/api/v1/public
```

## 🔑 Authentication

Most public API endpoints require an API key:

```http
Authorization: Bearer YOUR_API_KEY
```

### Getting an API Key

1. Register at [https://app.ainflue.com](https://app.ainflue.com)
2. Navigate to Developer Settings
3. Generate a new API key
4. Copy and securely store your API key

## 📊 Rate Limits

| Tier | Per Minute | Per Hour | Per Day |
|------|------------|----------|---------|
| Free | 60 | 1,000 | 10,000 |
| Pro | 300 | 10,000 | 100,000 |
| Enterprise | Custom | Custom | Custom |

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Request limit for the current window
- `X-RateLimit-Remaining`: Remaining requests in current window  
- `X-RateLimit-Reset`: Unix timestamp when the limit resets

## 📚 API Endpoints

### Health & Information

#### `GET /health`
Check API health status (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-09T10:30:00Z",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "ai_engine": "healthy",
    "fingerprinting": "healthy"
  },
  "response_time_ms": 45.2
}
```

#### `GET /info`
Get SDK and API information (no authentication required).

**Response:**
```json
{
  "sdk_version": "1.0.0",
  "supported_languages": ["Python", "JavaScript", "REST API"],
  "endpoints": [
    "/public/health",
    "/public/info",
    "/public/docs",
    "/public/sandbox/test",
    "/public/content/analyze",
    "/public/content/fingerprint"
  ],
  "rate_limits": {
    "requests_per_minute": 60,
    "requests_per_hour": 1000,
    "requests_per_day": 10000
  },
  "documentation_url": "/public/docs",
  "download_urls": {
    "python_sdk": "/public/sdk/python",
    "javascript_sdk": "/public/sdk/javascript",
    "postman_collection": "/public/docs/postman"
  }
}
```

### Documentation

#### `GET /docs`
Get interactive API documentation (HTML page).

Returns a comprehensive HTML documentation page with:
- Available endpoints
- Authentication instructions
- SDK download links
- Rate limiting information
- Support contacts

### Sandbox Testing

#### `POST /sandbox/test`
Test API endpoints in a safe sandbox environment.

**Authentication:** Required  
**Request Body:**
```json
{
  "endpoint": "/public/health",
  "method": "GET",
  "payload": {},
  "headers": {}
}
```

**Response:**
```json
{
  "test_id": "test_12345",
  "endpoint": "/public/health",
  "method": "GET",
  "status_code": 200,
  "response_time_ms": 12.5,
  "response_data": {
    "status": "healthy",
    "timestamp": "2025-01-09T10:30:00Z"
  },
  "timestamp": "2025-01-09T10:30:00Z"
}
```

### Content Analysis

#### `POST /content/analyze`
Analyze uploaded content for protection and insights.

**Authentication:** Required  
**Content-Type:** `multipart/form-data`  
**Body:** File upload (max 50MB for public API)

**Response:**
```json
{
  "content_id": "content_67890",
  "filename": "my_audio.mp3",
  "content_type": "audio/mpeg",
  "file_size": 1024000,
  "analysis": {
    "is_valid": true,
    "detected_format": "audio/mpeg",
    "estimated_duration": 180.5,
    "quality_score": 0.85,
    "protection_recommended": true
  },
  "fingerprint_available": true,
  "analyzed_at": "2025-01-09T10:30:00Z"
}
```

#### `POST /content/fingerprint`
Generate fingerprint for content protection.

**Authentication:** Required  
**Content-Type:** `multipart/form-data`  
**Body:** File upload (max 50MB for public API)

**Response:**
```json
{
  "fingerprint_id": "fp_abc123",
  "content_hash": "fp_abc123def456",
  "algorithm": "ainflue-v1",
  "confidence_score": 0.95,
  "processing_time": 2.1,
  "created_at": "2025-01-09T10:30:00Z",
  "protection_features": [
    "watermarking",
    "duplicate_detection", 
    "usage_tracking"
  ]
}
```

### SDK Downloads

#### `GET /sdk/python`
Download Python SDK source code.

**Response:**
```json
{
  "filename": "ainflue_sdk.py",
  "content": "# SDK source code here...",
  "version": "1.0.0",
  "installation": "pip install ainflue-sdk",
  "documentation": "/public/docs"
}
```

#### `GET /docs/postman`
Download Postman collection for API testing.

**Response:** JSON Postman collection with pre-configured requests for all public API endpoints.

## 🛠️ SDK Integration

### Python SDK

```python
from ainflue_sdk import create_sdk

async def main():
    async with create_sdk(api_key="your-api-key") as sdk:
        # Check API health
        health = await sdk.get("/public/health")
        print(f"API Status: {health['status']}")
        
        # Analyze content
        with open("my_file.mp3", "rb") as f:
            result = await sdk.post_file("/public/content/analyze", {"file": f})
        print(f"Analysis: {result['analysis']['quality_score']}")

import asyncio
asyncio.run(main())
```

### JavaScript SDK (Coming Soon)

```javascript
import { AinflueSdk } from 'ainflue-sdk-js';

const sdk = new AinflueSdk({ apiKey: 'your-api-key' });

// Check API health
const health = await sdk.get('/public/health');
console.log(`API Status: ${health.status}`);

// Analyze content
const formData = new FormData();
formData.append('file', fileInput.files[0]);
const result = await sdk.post('/public/content/analyze', formData);
console.log(`Quality Score: ${result.analysis.quality_score}`);
```

### cURL Examples

```bash
# Check API health (no auth)
curl -X GET "https://api.ainflue.com/api/v1/public/health"

# Get API info (no auth)
curl -X GET "https://api.ainflue.com/api/v1/public/info"

# Test endpoint in sandbox
curl -X POST "https://api.ainflue.com/api/v1/public/sandbox/test" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/public/health", "method": "GET"}'

# Analyze content
curl -X POST "https://api.ainflue.com/api/v1/public/content/analyze" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@my_audio.mp3"

# Generate fingerprint
curl -X POST "https://api.ainflue.com/api/v1/public/content/fingerprint" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@my_audio.mp3"
```

## 🚨 Error Handling

All endpoints return standard HTTP status codes with detailed error information:

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "File size exceeds maximum limit",
    "details": {
      "max_size": "50MB",
      "received_size": "75MB"
    },
    "timestamp": "2025-01-09T10:30:00Z",
    "request_id": "req_12345"
  }
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `VALIDATION_ERROR` | Invalid request parameters |
| 401 | `AUTHENTICATION_ERROR` | Invalid or missing API key |
| 403 | `PERMISSION_DENIED` | Insufficient permissions |
| 413 | `FILE_TOO_LARGE` | File exceeds size limit |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |

## 🔧 Testing & Development

### Sandbox Environment

Use the `/sandbox/test` endpoint to safely test API calls without affecting production data:

```python
# Test any endpoint safely
test_result = await sdk.post("/public/sandbox/test", {
    "endpoint": "/public/content/analyze",
    "method": "POST",
    "payload": {"test": "data"}
})
```

### Development Tips

1. **Start with Health Check**: Always test `/public/health` first
2. **Use Sandbox**: Test complex workflows in sandbox before production
3. **Monitor Rate Limits**: Check response headers for rate limit status
4. **Handle Errors Gracefully**: Implement retry logic with exponential backoff
5. **Cache Responses**: Cache stable data like API info to reduce requests

## 📞 Support

- **Documentation**: [https://docs.ainflue.com](https://docs.ainflue.com)
- **API Status**: [https://status.ainflue.com](https://status.ainflue.com)
- **Support Email**: [mlaiel@live.de](mailto:mlaiel@live.de)
- **GitHub Issues**: [https://github.com/Mlaiel/Ainflue/issues](https://github.com/Mlaiel/Ainflue/issues)

## 📅 Changelog

### v1.0.0 (2025-01-09)
- Initial public API release
- Health check and info endpoints
- Sandbox testing environment
- Content analysis and fingerprinting
- SDK download endpoints
- Comprehensive documentation
- Rate limiting and error handling

---

**© 2025 Fahed Mlaiel. All rights reserved.**