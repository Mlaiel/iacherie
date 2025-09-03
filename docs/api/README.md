# 📚 Ainflue API Documentation Hub

Welcome to the comprehensive API documentation for the Ainflue AI Platform - your complete guide to integrating content protection, monetization, and AI-powered features.

## 🎯 Documentation Overview

This documentation covers all aspects of the Ainflue API v2.0, providing everything you need to build robust integrations with our platform.

## 📋 Complete Documentation Suite

### 🔧 Core API Documentation

| Document | Description | Use Case |
|----------|-------------|----------|
| **[OpenAPI Specification](./openapi-spec-complete.yaml)** | Complete OpenAPI 3.0 spec with all endpoints | API reference, code generation |
| **[API Reference](./API_REFERENCE.md)** | Human-readable API documentation | Development guide |
| **[Postman Collection](./ainflue-api-collection.json)** | Ready-to-use Postman requests | Testing, exploration |
| **[Postman Environment](./ainflue-api-environment.json)** | Environment variables for testing | Configuration |

### 📖 Guides & Best Practices

| Document | Description | Use Case |
|----------|-------------|----------|
| **[API Versioning Guide](./API_VERSIONING_GUIDE.md)** | Version management and migration | Upgrades, compatibility |
| **[Rate Limiting Guide](./RATE_LIMITING_GUIDE.md)** | Rate limits and optimization | Performance, scaling |
| **[Error Codes Reference](./ERROR_CODES_REFERENCE.md)** | Complete error handling guide | Debugging, error handling |

### 🛠️ Development Tools

| File | Description | Use Case |
|------|-------------|----------|
| **[Postman Generator](./generate_postman_collection.py)** | Auto-generate Postman collections | Automation, updates |

## 🚀 Quick Start Guide

### 1. Choose Your Integration Method

#### Option A: Postman Collection (Recommended for Testing)
```bash
# Import collection and environment files into Postman
1. Download: ainflue-api-collection.json
2. Download: ainflue-api-environment.json  
3. Import both files into Postman
4. Configure environment variables
5. Start testing endpoints
```

#### Option B: OpenAPI Specification (Recommended for Development)
```bash
# Use with your favorite OpenAPI tools
swagger-codegen generate \
  -i openapi-spec-complete.yaml \
  -l python \
  -o ./ainflue-python-client

# Or use with OpenAPI Generator
openapi-generator-cli generate \
  -i openapi-spec-complete.yaml \
  -g typescript-axios \
  -o ./ainflue-typescript-client
```

#### Option C: Direct API Integration
```bash
# Base URL
https://api.ainflue.com/v2

# Authentication
Authorization: Bearer <your_jwt_token>
# OR
X-API-Key: <your_api_key>
```

## 🔐 Authentication

### Authentication Methods
- **JWT Bearer Tokens**: Primary authentication method
- **OAuth 2.0**: Third-party application integration
- **API Keys**: Server-to-server communication

### Authentication Endpoints

#### POST /api/v1/auth/login
Authenticate user and receive access token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123!",
  "remember_me": false
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "profile_type": "creator",
    "verified": true
  }
}
```

#### POST /api/v1/auth/refresh
Refresh expired access token.

**Request:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 🛡️ Content Protection API

### Content Upload and Analysis

#### POST /api/v1/content/upload
Upload content for AI-powered protection and analysis.

**Request:**
```bash
curl -X POST \
  https://api.ainflue.com/v1/content/upload \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio_track.mp3" \
  -F "metadata={\"title\":\"My Song\",\"description\":\"Original composition\"}"
```

**Response:**
```json
{
  "content_id": "uuid-string",
  "fingerprint_id": "fp_uuid",
  "analysis_status": "processing",
  "protection_enabled": true,
  "metadata": {
    "title": "My Song",
    "duration": 180.5,
    "file_size": 5242880,
    "format": "mp3",
    "quality": "320kbps"
  },
  "ai_analysis": {
    "genre_detected": "electronic",
    "mood": "energetic",
    "instruments": ["synthesizer", "drums"],
    "confidence_score": 0.92
  }
}
```

#### GET /api/v1/content/{content_id}/protection-status
Get real-time protection status for content.

**Response:**
```json
{
  "content_id": "uuid-string",
  "protection_status": "active",
  "monitoring_platforms": ["youtube", "soundcloud", "spotify", "tiktok"],
  "violations_detected": 3,
  "revenue_protected": 1250.50,
  "last_scan": "2024-01-15T10:30:00Z",
  "next_scan": "2024-01-15T11:00:00Z"
}
```

### Violation Management

#### GET /api/v1/violations
List content violations detected across platforms.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `status`: Filter by status (pending, resolved, dismissed)
- `platform`: Filter by platform
- `content_id`: Filter by specific content

**Response:**
```json
{
  "violations": [
    {
      "violation_id": "uuid-string",
      "content_id": "uuid-string",
      "platform": "youtube",
      "violation_url": "https://youtube.com/watch?v=example",
      "similarity_score": 0.95,
      "detected_at": "2024-01-15T09:15:00Z",
      "status": "pending",
      "estimated_revenue_loss": 125.75,
      "automated_action": "takedown_requested",
      "manual_review_required": false
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_pages": 5,
    "total_count": 87
  }
}
```

#### POST /api/v1/violations/{violation_id}/action
Take action on a detected violation.

**Request:**
```json
{
  "action": "takedown_request",
  "notes": "Clear copyright infringement",
  "priority": "high"
}
```

## 💰 Monetization API

### Revenue Tracking

#### GET /api/v1/revenue/summary
Get comprehensive revenue summary.

**Query Parameters:**
- `period`: Time period (day, week, month, year)
- `start_date`: Start date (ISO 8601)
- `end_date`: End date (ISO 8601)

**Response:**
```json
{
  "summary": {
    "total_revenue": 15420.75,
    "period_revenue": 2340.50,
    "revenue_growth": 0.15,
    "active_content_count": 142,
    "platform_breakdown": {
      "youtube": 8500.25,
      "spotify": 4200.30,
      "soundcloud": 1850.20,
      "other": 870.00
    }
  },
  "top_performing_content": [
    {
      "content_id": "uuid-string",
      "title": "Hit Song",
      "revenue": 850.75,
      "views": 125000,
      "platforms": ["youtube", "spotify"]
    }
  ]
}
```

### Payment Management

#### GET /api/v1/payments/history
Get payment history and upcoming payouts.

**Response:**
```json
{
  "payments": [
    {
      "payment_id": "uuid-string",
      "amount": 1250.50,
      "currency": "USD",
      "status": "completed",
      "payment_date": "2024-01-01T00:00:00Z",
      "payment_method": "bank_transfer",
      "transaction_fee": 25.01
    }
  ],
  "upcoming_payout": {
    "amount": 890.25,
    "scheduled_date": "2024-02-01T00:00:00Z",
    "minimum_threshold": 100.00
  }
}
```

## 📊 Analytics API

### Performance Analytics

#### GET /api/v1/analytics/performance
Get detailed performance analytics for content.

**Query Parameters:**
- `content_id`: Specific content (optional)
- `metrics`: Comma-separated metrics (views, engagement, revenue)
- `granularity`: Data granularity (hour, day, week, month)

**Response:**
```json
{
  "analytics": {
    "content_id": "uuid-string",
    "period": "30_days",
    "metrics": {
      "total_views": 1250000,
      "unique_viewers": 890000,
      "engagement_rate": 0.078,
      "average_watch_time": 145.5,
      "revenue_per_view": 0.0012
    },
    "platform_performance": {
      "youtube": {
        "views": 850000,
        "engagement_rate": 0.085,
        "revenue": 1020.50
      },
      "spotify": {
        "plays": 400000,
        "save_rate": 0.032,
        "revenue": 480.75
      }
    },
    "geographic_breakdown": {
      "US": 0.45,
      "UK": 0.18,
      "CA": 0.12,
      "other": 0.25
    }
  }
}
```

### Audience Insights

#### GET /api/v1/analytics/audience
Get audience demographics and behavior insights.

**Response:**
```json
{
  "audience_insights": {
    "demographics": {
      "age_groups": {
        "18-24": 0.35,
        "25-34": 0.40,
        "35-44": 0.20,
        "45+": 0.05
      },
      "gender_distribution": {
        "male": 0.52,
        "female": 0.46,
        "other": 0.02
      }
    },
    "behavior_patterns": {
      "peak_listening_hours": [19, 20, 21],
      "preferred_platforms": ["youtube", "spotify", "soundcloud"],
      "engagement_trends": {
        "comments": 0.15,
        "shares": 0.08,
        "saves": 0.25
      }
    },
    "content_preferences": {
      "genres": {
        "electronic": 0.45,
        "pop": 0.30,
        "rock": 0.25
      },
      "content_length": {
        "short_form": 0.60,
        "medium_form": 0.35,
        "long_form": 0.05
      }
    }
  }
}
```

## 🤝 Collaboration API

### Creator Matching

#### GET /api/v1/collaboration/matches
Get AI-powered collaboration matches.

**Query Parameters:**
- `genre`: Preferred genre
- `collaboration_type`: remix, feature, duet, etc.
- `experience_level`: beginner, intermediate, professional

**Response:**
```json
{
  "matches": [
    {
      "creator_id": "uuid-string",
      "username": "music_producer_pro",
      "compatibility_score": 0.89,
      "shared_interests": ["electronic", "ambient", "experimental"],
      "collaboration_history": 12,
      "avg_rating": 4.8,
      "recent_work": [
        {
          "title": "Synth Dreams",
          "views": 45000,
          "collaboration_type": "remix"
        }
      ],
      "preferred_collaboration": ["remix", "original_composition"]
    }
  ]
}
```

#### POST /api/v1/collaboration/invite
Send collaboration invitation to another creator.

**Request:**
```json
{
  "target_creator_id": "uuid-string",
  "collaboration_type": "remix",
  "content_id": "uuid-string",
  "message": "I'd love to collaborate on a remix of this track!",
  "revenue_split": {
    "initiator": 0.6,
    "collaborator": 0.4
  }
}
```

## 🔍 Search and Discovery API

### Content Search

#### GET /api/v1/search/content
Search for content across the platform.

**Query Parameters:**
- `q`: Search query
- `type`: Content type (audio, video, image)
- `genre`: Filter by genre
- `sort`: Sort order (relevance, date, popularity)

**Response:**
```json
{
  "results": [
    {
      "content_id": "uuid-string",
      "title": "Electronic Vibes",
      "creator": "dj_electric",
      "genre": "electronic",
      "duration": 245,
      "views": 125000,
      "relevance_score": 0.95,
      "thumbnail_url": "https://cdn.ainflue.com/thumbnails/...",
      "preview_url": "https://cdn.ainflue.com/previews/..."
    }
  ],
  "filters": {
    "available_genres": ["electronic", "pop", "rock"],
    "duration_ranges": ["0-60", "60-180", "180+"],
    "popularity_ranges": ["viral", "trending", "emerging"]
  }
}
```

## 📱 Platform Integration API

### Social Media Publishing

#### POST /api/v1/integrations/publish
Publish content to connected social media platforms.

**Request:**
```json
{
  "content_id": "uuid-string",
  "platforms": ["youtube", "tiktok", "instagram"],
  "metadata": {
    "title": "My Latest Track",
    "description": "Check out my new electronic music!",
    "tags": ["electronic", "music", "original"],
    "scheduled_time": "2024-01-16T18:00:00Z"
  },
  "optimization": {
    "auto_optimize_title": true,
    "auto_generate_tags": true,
    "platform_specific_formatting": true
  }
}
```

**Response:**
```json
{
  "publication_id": "uuid-string",
  "status": "scheduled",
  "platform_results": {
    "youtube": {
      "status": "scheduled",
      "publication_id": "yt_uuid",
      "scheduled_time": "2024-01-16T18:00:00Z",
      "optimized_title": "My Latest Track - Electronic Music 2024"
    },
    "tiktok": {
      "status": "published",
      "publication_id": "tt_uuid",
      "url": "https://tiktok.com/@user/video/...",
      "optimized_description": "New electronic track! 🎵 #electronic #music"
    }
  }
}
```

## 📈 SEO and Optimization API

### SEO Analysis

#### GET /api/v1/seo/analysis/{content_id}
Get SEO analysis and optimization recommendations.

**Response:**
```json
{
  "seo_analysis": {
    "content_id": "uuid-string",
    "overall_score": 85,
    "recommendations": [
      {
        "category": "title_optimization",
        "priority": "high",
        "suggestion": "Include trending keywords 'electronic music 2024'",
        "impact_score": 0.75
      },
      {
        "category": "description",
        "priority": "medium",
        "suggestion": "Add more descriptive tags about instruments used",
        "impact_score": 0.45
      }
    ],
    "keyword_analysis": {
      "primary_keywords": ["electronic", "music", "original"],
      "trending_keywords": ["ambient", "chill", "study music"],
      "search_volume": {
        "electronic music": 125000,
        "ambient electronic": 45000
      }
    },
    "platform_optimization": {
      "youtube": {
        "title_score": 90,
        "description_score": 75,
        "tags_score": 80
      },
      "spotify": {
        "metadata_score": 85,
        "playlist_potential": 0.78
      }
    }
  }
}
```

## 🔄 Webhook API

### Event Notifications

#### POST /webhooks/setup
Configure webhook endpoints for real-time notifications.

**Request:**
```json
{
  "endpoint_url": "https://yourapp.com/ainflue-webhook",
  "events": [
    "content.uploaded",
    "violation.detected",
    "payment.completed",
    "collaboration.invited"
  ],
  "secret": "webhook_secret_key",
  "active": true
}
```

### Webhook Event Examples

#### Content Upload Event
```json
{
  "event": "content.uploaded",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "content_id": "uuid-string",
    "user_id": "uuid-string",
    "title": "New Track",
    "status": "processing",
    "protection_enabled": true
  }
}
```

#### Violation Detection Event
```json
{
  "event": "violation.detected",
  "timestamp": "2024-01-15T11:15:00Z",
  "data": {
    "violation_id": "uuid-string",
    "content_id": "uuid-string",
    "platform": "youtube",
    "similarity_score": 0.95,
    "automated_action": "takedown_requested"
  }
}
```

## 📊 Rate Limits and Quotas

### Rate Limiting

| Endpoint Category | Rate Limit | Burst Limit |
|------------------|------------|-------------|
| Authentication | 5 req/min | 10 |
| Content Upload | 10 req/hour | 20 |
| API Queries | 100 req/min | 200 |
| Analytics | 50 req/min | 100 |
| Webhooks | 1000 req/min | 2000 |

### Usage Quotas

| Plan Tier | Monthly API Calls | Storage (GB) | Processing Hours |
|-----------|------------------|--------------|------------------|
| Free | 1,000 | 1 | 5 |
| Pro | 50,000 | 50 | 100 |
| Enterprise | Unlimited | 1,000 | 1,000 |

## 🔧 SDKs and Libraries

### Official SDKs

#### JavaScript/Node.js
```bash
npm install @ainflue/api-client
```

```javascript
import { AinfluenceClient } from '@ainflue/api-client';

const client = new AinfluenceClient({
  apiKey: 'your-api-key',
  environment: 'production' // or 'sandbox'
});

// Upload content
const result = await client.content.upload({
  file: fileBuffer,
  metadata: {
    title: 'My Song',
    genre: 'electronic'
  }
});
```

#### Python
```bash
pip install ainflue-api
```

```python
from ainflue import AinfluenceClient

client = AinfluenceClient(
    api_key='your-api-key',
    environment='production'
)

# Get revenue summary
revenue = client.revenue.get_summary(period='month')
print(f"Total revenue: ${revenue.total_revenue}")
```

## 🚨 Error Handling

### Standard Error Response Format
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request parameters are invalid",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    },
    "request_id": "req_uuid",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| UNAUTHORIZED | 401 | Invalid or expired authentication |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| RATE_LIMITED | 429 | Rate limit exceeded |
| VALIDATION_ERROR | 400 | Request validation failed |
| SERVER_ERROR | 500 | Internal server error |
| SERVICE_UNAVAILABLE | 503 | Service temporarily unavailable |

## 📞 Support and Resources

### API Support
- **Documentation**: https://docs.ainflue.com/api
- **Status Page**: https://status.ainflue.com
- **Support Email**: api-support@ainflue.com
- **Developer Discord**: https://discord.gg/ainflue-dev

### Testing Environment
- **Sandbox URL**: https://api-sandbox.ainflue.com
- **Test API Keys**: Available in developer dashboard
- **Mock Data**: Pre-populated test data available

---

**API Version**: v1  
**Last Updated**: {{current_date}}  
**Documentation Version**: 1.0.0

---

> **Note**: This API documentation is continuously updated. Subscribe to our developer newsletter for the latest updates and new feature announcements.