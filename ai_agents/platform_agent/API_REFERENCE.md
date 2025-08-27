# Platform Agent - API Reference

**Author**: Fahed Mlaiel <mlaiel@live.de>  
**Copyright**: © 2025 Fahed Mlaiel. All rights reserved.  
**Version**: 1.0.0  

⚠️ **LEGAL NOTICE**: This code and all associated intellectual property are exclusively owned by Fahed Mlaiel. Unauthorized use is strictly prohibited.

## 📋 Table of Contents

- [Authentication](#authentication)
- [Core APIs](#core-apis)
- [Platform Management](#platform-management)
- [Content Operations](#content-operations)
- [Analytics & Metrics](#analytics--metrics)
- [Synchronization](#synchronization)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [WebSocket Events](#websocket-events)

## 🔐 Authentication

### Bearer Token Authentication

All API requests require a valid Bearer token in the Authorization header:

```http
Authorization: Bearer <your_access_token>
```

### Obtaining Access Token

```http
POST /api/v1/auth/token
Content-Type: application/json

{
    "username": "user@example.com",
    "password": "secure_password",
    "platform_permissions": ["spotify", "youtube", "instagram"]
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": ["platform:read", "platform:write", "analytics:read"]
}
```

## 🚀 Core APIs

### Platform Agent Management

#### Create Platform Agent

```http
POST /api/v1/agents
Content-Type: application/json
Authorization: Bearer <token>

{
    "agent_id": "influencer_001",
    "platforms": ["spotify", "youtube", "instagram"],
    "config": {
        "enable_ai_optimization": true,
        "enable_real_time_sync": true,
        "optimization_level": "advanced",
        "security_level": "enterprise"
    }
}
```

**Response:**
```json
{
    "agent_id": "influencer_001",
    "status": "created",
    "platforms": [
        {
            "platform": "spotify",
            "status": "connected",
            "health": "healthy"
        },
        {
            "platform": "youtube", 
            "status": "connected",
            "health": "healthy"
        }
    ],
    "created_at": "2025-08-11T10:30:00Z"
}
```

#### Get Agent Status

```http
GET /api/v1/agents/{agent_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
    "agent_id": "influencer_001",
    "status": "active",
    "platforms": {
        "spotify": {
            "status": "connected",
            "health": "healthy",
            "last_sync": "2025-08-11T10:25:00Z",
            "rate_limit_remaining": 95
        }
    },
    "metrics": {
        "total_uploads": 150,
        "success_rate": 98.5,
        "avg_response_time": 250
    }
}
```

## 📤 Content Operations

### Upload Content

```http
POST /api/v1/content/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- file: audio_track.mp3
- platforms: ["spotify", "youtube"]
- metadata: {
    "title": "AI Generated Symphony",
    "description": "A beautiful AI composition",
    "tags": ["ai", "music", "symphony"],
    "category": "Music",
    "privacy": "public",
    "language": "en",
    "copyright_notice": "© 2025 Fahed Mlaiel"
}
```

**Response:**
```json
{
    "upload_id": "upload_abc123",
    "status": "processing",
    "platform_results": {
        "spotify": {
            "status": "queued",
            "estimated_completion": "2025-08-11T10:35:00Z"
        },
        "youtube": {
            "status": "processing",
            "progress": 25,
            "estimated_completion": "2025-08-11T10:40:00Z"
        }
    },
    "ai_optimization": {
        "enabled": true,
        "enhancements": ["audio_quality", "metadata_seo", "thumbnail_generation"]
    }
}
```

### Get Upload Status

```http
GET /api/v1/content/upload/{upload_id}/status
Authorization: Bearer <token>
```

**Response:**
```json
{
    "upload_id": "upload_abc123",
    "overall_status": "completed",
    "platform_results": {
        "spotify": {
            "status": "published",
            "platform_id": "spotify_track_xyz789",
            "url": "https://open.spotify.com/track/xyz789",
            "published_at": "2025-08-11T10:32:00Z"
        },
        "youtube": {
            "status": "published", 
            "platform_id": "youtube_video_abc456",
            "url": "https://www.youtube.com/watch?v=abc456",
            "published_at": "2025-08-11T10:38:00Z"
        }
    }
}
```

### Update Content

```http
PATCH /api/v1/content/{content_id}
Content-Type: application/json
Authorization: Bearer <token>

{
    "platforms": ["spotify", "youtube"],
    "updates": {
        "title": "Updated Track Title",
        "description": "Updated description with new information",
        "tags": ["ai", "music", "updated"]
    }
}
```

### Delete Content

```http
DELETE /api/v1/content/{content_id}
Authorization: Bearer <token>
```

**Query Parameters:**
- `platforms`: Comma-separated list of platforms (optional, defaults to all)
- `permanent`: Boolean, whether to permanently delete (default: false)

## 📊 Analytics & Metrics

### Get Platform Analytics

```http
GET /api/v1/analytics/{platform}
Authorization: Bearer <token>
```

**Query Parameters:**
- `start_date`: ISO date string (e.g., "2025-01-01")
- `end_date`: ISO date string (e.g., "2025-08-11")
- `content_type`: Filter by content type
- `metrics`: Comma-separated list of specific metrics

**Response:**
```json
{
    "platform": "spotify",
    "date_range": {
        "start": "2025-01-01T00:00:00Z",
        "end": "2025-08-11T23:59:59Z"
    },
    "summary": {
        "total_content": 45,
        "total_plays": 125000,
        "total_likes": 8500,
        "total_shares": 1200,
        "engagement_rate": 7.8,
        "reach": 95000,
        "impressions": 280000
    },
    "content_performance": [
        {
            "content_id": "content_123",
            "title": "AI Symphony No. 1",
            "plays": 15000,
            "likes": 1200,
            "shares": 180,
            "engagement_rate": 9.2
        }
    ],
    "trends": {
        "plays_trend": "+15%",
        "engagement_trend": "+22%",
        "top_performing_tags": ["ai", "instrumental", "electronic"]
    }
}
```

### Get Cross-Platform Analytics

```http
GET /api/v1/analytics/cross-platform
Authorization: Bearer <token>
```

**Response:**
```json
{
    "total_metrics": {
        "platforms": 5,
        "total_content": 180,
        "total_engagement": 95000,
        "average_engagement_rate": 8.4
    },
    "platform_comparison": {
        "spotify": {
            "content_count": 45,
            "engagement_rate": 7.8,
            "top_content_type": "audio"
        },
        "youtube": {
            "content_count": 38,
            "engagement_rate": 9.1,
            "top_content_type": "video"
        }
    },
    "insights": {
        "best_performing_platform": "youtube",
        "optimal_posting_time": "18:00 UTC",
        "trending_topics": ["ai music", "electronic", "ambient"]
    }
}
```

## 🔄 Platform Management

### Connect Platform

```http
POST /api/v1/platforms/connect
Content-Type: application/json
Authorization: Bearer <token>

{
    "platform": "spotify",
    "credentials": {
        "client_id": "spotify_client_id",
        "client_secret": "spotify_client_secret",
        "redirect_uri": "https://your-app.com/callback"
    }
}
```

**Response:**
```json
{
    "platform": "spotify",
    "status": "connected",
    "auth_url": "https://accounts.spotify.com/authorize?...",
    "connection_id": "conn_spotify_123"
}
```

### Disconnect Platform

```http
DELETE /api/v1/platforms/{platform}/disconnect
Authorization: Bearer <token>
```

### Get Platform Health

```http
GET /api/v1/platforms/{platform}/health
Authorization: Bearer <token>
```

**Response:**
```json
{
    "platform": "spotify",
    "status": "healthy",
    "response_time": 245,
    "rate_limit": {
        "remaining": 95,
        "reset_at": "2025-08-11T11:00:00Z"
    },
    "last_successful_request": "2025-08-11T10:55:30Z",
    "error_rate": 0.5
}
```

## 🔄 Synchronization

### Trigger Manual Sync

```http
POST /api/v1/sync/trigger
Content-Type: application/json
Authorization: Bearer <token>

{
    "sync_type": "incremental",
    "platforms": ["spotify", "youtube"],
    "sync_direction": "bidirectional",
    "priority": "high"
}
```

**Response:**
```json
{
    "sync_id": "sync_abc123",
    "status": "started",
    "estimated_completion": "2025-08-11T11:05:00Z",
    "platforms": ["spotify", "youtube"]
}
```

### Get Sync Status

```http
GET /api/v1/sync/{sync_id}/status
Authorization: Bearer <token>
```

**Response:**
```json
{
    "sync_id": "sync_abc123",
    "status": "completed",
    "progress": 100,
    "started_at": "2025-08-11T10:58:00Z",
    "completed_at": "2025-08-11T11:03:00Z",
    "results": {
        "spotify": {
            "status": "success",
            "items_synced": 12,
            "conflicts_resolved": 1
        },
        "youtube": {
            "status": "success", 
            "items_synced": 8,
            "conflicts_resolved": 0
        }
    }
}
```

## ⚙️ System Management

### Get System Health

```http
GET /api/v1/health
Authorization: Bearer <token>
```

**Response:**
```json
{
    "overall_status": "healthy",
    "components": {
        "database": {
            "status": "healthy",
            "response_time": 15
        },
        "cache": {
            "status": "healthy",
            "response_time": 2
        },
        "ai_services": {
            "status": "healthy",
            "gpu_utilization": 45
        }
    },
    "platform_health": {
        "spotify": "healthy",
        "youtube": "healthy",
        "instagram": "degraded"
    },
    "timestamp": "2025-08-11T11:00:00Z"
}
```

### Get System Metrics

```http
GET /api/v1/metrics
Authorization: Bearer <token>
```

**Response:**
```json
{
    "performance": {
        "avg_response_time": 180,
        "requests_per_minute": 450,
        "error_rate": 0.2,
        "uptime": "99.95%"
    },
    "resource_usage": {
        "cpu_usage": 35,
        "memory_usage": 2048,
        "disk_usage": 45,
        "network_io": 1250
    },
    "business_metrics": {
        "active_users": 1250,
        "daily_uploads": 3400,
        "total_content_items": 125000
    }
}
```

## 🚨 Error Handling

### Standard Error Response

```json
{
    "error": {
        "code": "UPLOAD_FAILED",
        "message": "Failed to upload content to platform",
        "details": {
            "platform": "spotify",
            "reason": "Invalid file format",
            "supported_formats": ["mp3", "wav", "flac"]
        },
        "user_message": "The audio file format is not supported. Please use MP3, WAV, or FLAC format.",
        "timestamp": "2025-08-11T11:00:00Z",
        "request_id": "req_abc123"
    }
}
```

### HTTP Status Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200  | OK | Successful request |
| 201  | Created | Resource created successfully |
| 202  | Accepted | Request accepted for processing |
| 400  | Bad Request | Invalid request format |
| 401  | Unauthorized | Invalid or missing authentication |
| 403  | Forbidden | Insufficient permissions |
| 404  | Not Found | Resource not found |
| 409  | Conflict | Resource conflict |
| 429  | Too Many Requests | Rate limit exceeded |
| 500  | Internal Server Error | Server error |
| 502  | Bad Gateway | Platform API error |
| 503  | Service Unavailable | Service temporarily unavailable |

### Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| `INVALID_TOKEN` | Authentication token is invalid | Refresh token or re-authenticate |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait for reset time |
| `PLATFORM_UNAVAILABLE` | Platform API is down | Retry later |
| `UPLOAD_FAILED` | Content upload failed | Check file format and size |
| `SYNC_CONFLICT` | Data synchronization conflict | Manual resolution required |
| `INSUFFICIENT_PERMISSIONS` | Missing required permissions | Update platform permissions |

## ⏱️ Rate Limiting

### Rate Limit Headers

All API responses include rate limit information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1628687400
X-RateLimit-RetryAfter: 3600
```

### Rate Limit Tiers

| Tier | Requests/Hour | Concurrent Uploads | Burst Limit |
|------|---------------|-------------------|-------------|
| Basic | 1,000 | 5 | 50 |
| Professional | 10,000 | 20 | 200 |
| Enterprise | 100,000 | 100 | 1,000 |

### Rate Limit Exceeded Response

```json
{
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Rate limit exceeded",
        "details": {
            "limit": 1000,
            "remaining": 0,
            "reset_at": "2025-08-11T12:00:00Z"
        },
        "retry_after": 3600
    }
}
```

## 🔌 WebSocket Events

### Connection

```javascript
const ws = new WebSocket('wss://api.platform-agent.com/ws');
ws.onopen = () => {
    ws.send(JSON.stringify({
        type: 'auth',
        token: 'your_access_token'
    }));
};
```

### Upload Progress

```json
{
    "type": "upload_progress",
    "data": {
        "upload_id": "upload_abc123",
        "progress": 75,
        "platform": "spotify",
        "estimated_completion": "2025-08-11T11:05:00Z"
    }
}
```

### Platform Status

```json
{
    "type": "platform_status",
    "data": {
        "platform": "youtube",
        "status": "degraded",
        "message": "Experiencing high latency",
        "timestamp": "2025-08-11T11:00:00Z"
    }
}
```

### Sync Events

```json
{
    "type": "sync_event", 
    "data": {
        "sync_id": "sync_abc123",
        "status": "completed",
        "platforms": ["spotify", "youtube"],
        "items_synced": 20,
        "conflicts": 0
    }
}
```

### Real-time Analytics

```json
{
    "type": "analytics_update",
    "data": {
        "content_id": "content_123",
        "platform": "spotify",
        "plays": 1500,
        "likes": 120,
        "engagement_rate": 8.0
    }
}
```

## 📝 Request/Response Examples

### Batch Upload

```http
POST /api/v1/content/batch-upload
Content-Type: application/json
Authorization: Bearer <token>

{
    "uploads": [
        {
            "file_url": "https://storage.example.com/audio1.mp3",
            "platforms": ["spotify", "youtube"],
            "metadata": {
                "title": "Track 1",
                "description": "First track"
            }
        },
        {
            "file_url": "https://storage.example.com/audio2.mp3", 
            "platforms": ["spotify"],
            "metadata": {
                "title": "Track 2",
                "description": "Second track"
            }
        }
    ]
}
```

### Search Content

```http
GET /api/v1/content/search?q=ai%20music&platforms=spotify,youtube&limit=20
Authorization: Bearer <token>
```

### Content Optimization

```http
POST /api/v1/content/{content_id}/optimize
Content-Type: application/json
Authorization: Bearer <token>

{
    "optimization_level": "ai_enhanced",
    "target_platforms": ["instagram", "tiktok"],
    "enhancements": ["audio_quality", "thumbnail_generation", "seo_metadata"]
}
```

## 🔐 Security Features

### API Key Management

```http
POST /api/v1/api-keys
Content-Type: application/json
Authorization: Bearer <token>

{
    "name": "Mobile App Key",
    "permissions": ["content:read", "analytics:read"],
    "expires_at": "2025-12-31T23:59:59Z"
}
```

### Webhook Signatures

All webhook payloads are signed with HMAC-SHA256:

```http
X-Signature-SHA256: sha256=1234567890abcdef...
```

Verify signature:
```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={expected}" == signature
```

## 📚 SDK Examples

### Python SDK

```python
from platform_agent_sdk import PlatformAgentClient

client = PlatformAgentClient(api_key='your_api_key')

# Upload content
result = await client.upload_content(
    file_path='track.mp3',
    platforms=['spotify', 'youtube'],
    metadata={
        'title': 'AI Symphony',
        'description': 'AI-generated music'
    }
)

# Get analytics
analytics = await client.get_analytics(
    platform='spotify',
    start_date='2025-01-01',
    end_date='2025-08-11'
)
```

### JavaScript SDK

```javascript
import { PlatformAgentClient } from '@platform-agent/sdk';

const client = new PlatformAgentClient({
    apiKey: 'your_api_key',
    baseUrl: 'https://api.platform-agent.com'
});

// Upload content
const result = await client.uploadContent({
    filePath: 'track.mp3',
    platforms: ['spotify', 'youtube'],
    metadata: {
        title: 'AI Symphony',
        description: 'AI-generated music'
    }
});
```

---

## 📄 Legal & Copyright

**© 2025 Fahed Mlaiel. All Rights Reserved.**

This API documentation and all associated code are proprietary and confidential. Unauthorized use, reproduction, or distribution is strictly prohibited.

**Contact**: mlaiel@live.de  
**License**: Commercial license required for production use

---

*Last updated: August 11, 2025*
