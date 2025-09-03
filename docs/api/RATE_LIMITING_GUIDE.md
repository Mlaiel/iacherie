# 🚦 Rate Limiting Guide - Ainflue API

## 🎯 Overview

The Ainflue API implements comprehensive rate limiting to ensure fair usage, maintain service quality, and protect against abuse. This guide covers all aspects of our rate limiting system.

## 📊 Rate Limiting Tiers

### Free Tier
- **Request Limit**: 1,000 requests per hour
- **Burst Limit**: 100 requests per minute
- **Content Upload**: 10 files per day (max 10MB each)
- **AI Processing**: 50 operations per day
- **Concurrent Requests**: 5

### Pro Tier
- **Request Limit**: 10,000 requests per hour  
- **Burst Limit**: 500 requests per minute
- **Content Upload**: 100 files per day (max 100MB each)
- **AI Processing**: 500 operations per day
- **Concurrent Requests**: 20

### Enterprise Tier
- **Request Limit**: 100,000 requests per hour
- **Burst Limit**: 2,000 requests per minute
- **Content Upload**: Unlimited (max 1GB each)
- **AI Processing**: 5,000 operations per day
- **Concurrent Requests**: 100

### Custom Enterprise
- **Request Limit**: Negotiated based on requirements
- **SLA Guarantees**: 99.9% uptime
- **Dedicated Resources**: Isolated infrastructure
- **Priority Support**: 24/7 technical support

## 🏗️ Rate Limiting Implementation

### Algorithm: Token Bucket + Fixed Window

We use a hybrid approach combining:
1. **Token Bucket**: For burst handling
2. **Fixed Window**: For hourly limits
3. **Sliding Window**: For complex endpoints

### Granularity Levels

1. **Global Rate Limits** (per API key/user)
2. **Endpoint-Specific Limits** (per endpoint)
3. **Feature-Based Limits** (AI processing, uploads)
4. **IP-Based Limits** (DDoS protection)

## 📋 Endpoint-Specific Limits

### Authentication Endpoints

| Endpoint | Free | Pro | Enterprise | Window |
|----------|------|-----|------------|--------|
| `POST /auth/login` | 10/hour | 50/hour | 200/hour | 1 hour |
| `POST /auth/register` | 5/hour | 20/hour | 100/hour | 1 hour |
| `POST /auth/refresh` | 50/hour | 200/hour | 1000/hour | 1 hour |
| `POST /auth/logout` | 20/hour | 100/hour | 500/hour | 1 hour |

### Content Management Endpoints

| Endpoint | Free | Pro | Enterprise | Window |
|----------|------|-----|------------|--------|
| `POST /content/upload` | 10/day | 100/day | Unlimited | 24 hours |
| `GET /content/{id}` | 500/hour | 2000/hour | 10000/hour | 1 hour |
| `PUT /content/{id}` | 20/hour | 100/hour | 500/hour | 1 hour |
| `DELETE /content/{id}` | 10/hour | 50/hour | 200/hour | 1 hour |
| `POST /content/{id}/analyze` | 50/day | 500/day | 5000/day | 24 hours |

### AI Fingerprinting Endpoints

| Endpoint | Free | Pro | Enterprise | Window |
|----------|------|-----|------------|--------|
| `POST /fingerprinting/generate` | 50/day | 500/day | 5000/day | 24 hours |
| `POST /fingerprinting/compare` | 100/day | 1000/day | 10000/day | 24 hours |

### Protection & Scanning Endpoints

| Endpoint | Free | Pro | Enterprise | Window |
|----------|------|-----|------------|--------|
| `POST /protection/scan` | 10/day | 100/day | 1000/day | 24 hours |
| `GET /protection/violations` | 200/hour | 1000/hour | 5000/hour | 1 hour |
| `PATCH /protection/violations/{id}` | 50/hour | 200/hour | 1000/hour | 1 hour |

### Analytics Endpoints

| Endpoint | Free | Pro | Enterprise | Window |
|----------|------|-----|------------|--------|
| `GET /analytics/dashboard` | 100/hour | 500/hour | 2000/hour | 1 hour |
| `GET /analytics/content/{id}/performance` | 50/hour | 200/hour | 1000/hour | 1 hour |

## 📡 Rate Limit Headers

All API responses include rate limiting information in headers:

### Standard Headers

```http
X-RateLimit-Limit: 1000          # Request limit for current window
X-RateLimit-Remaining: 987       # Requests remaining in current window  
X-RateLimit-Reset: 1704636000    # Unix timestamp when limit resets
X-RateLimit-Window: 3600         # Window duration in seconds
X-RateLimit-Tier: pro            # Current subscription tier
```

### Additional Headers

```http
X-RateLimit-Retry-After: 1800    # Seconds to wait before retry (when limited)
X-RateLimit-Burst-Limit: 100     # Burst limit for current window
X-RateLimit-Burst-Remaining: 45  # Remaining burst requests
X-RateLimit-Endpoint-Limit: 50   # Specific endpoint limit
X-RateLimit-Endpoint-Remaining: 30 # Remaining requests for specific endpoint
```

### Feature-Specific Headers

```http
X-RateLimit-Upload-Daily: 100         # Daily upload limit
X-RateLimit-Upload-Remaining: 75      # Remaining daily uploads
X-RateLimit-AI-Daily: 500            # Daily AI processing limit
X-RateLimit-AI-Remaining: 450        # Remaining AI operations
```

## ⚠️ Rate Limit Responses

### HTTP 429 - Too Many Requests

When rate limit is exceeded, the API returns:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1704636000
Retry-After: 1800

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Maximum 1000 requests per hour allowed.",
    "details": {
      "limit": 1000,
      "window": "hour",
      "retry_after": 1800,
      "tier": "free",
      "upgrade_url": "https://ainflue.com/pricing"
    },
    "request_id": "req_12345",
    "timestamp": "2025-01-07T10:00:00Z"
  }
}
```

### HTTP 503 - Service Unavailable

During system overload:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
Retry-After: 300

{
  "error": {
    "code": "SERVICE_OVERLOADED",
    "message": "Service temporarily unavailable due to high load",
    "details": {
      "retry_after": 300,
      "estimated_recovery": "2025-01-07T10:05:00Z"
    },
    "request_id": "req_12345",
    "timestamp": "2025-01-07T10:00:00Z"
  }
}
```

## 🛠️ Best Practices

### Client Implementation

1. **Respect Rate Limits**
   ```python
   import time
   import requests
   
   def api_request_with_retry(url, headers, max_retries=3):
       for attempt in range(max_retries):
           response = requests.get(url, headers=headers)
           
           if response.status_code == 429:
               retry_after = int(response.headers.get('Retry-After', 60))
               print(f"Rate limited. Waiting {retry_after} seconds...")
               time.sleep(retry_after)
               continue
               
           return response
       
       raise Exception("Max retries exceeded")
   ```

2. **Monitor Rate Limit Headers**
   ```python
   def check_rate_limits(response):
       remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
       reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
       
       if remaining < 10:
           wait_time = reset_time - int(time.time())
           print(f"Warning: Only {remaining} requests remaining")
           print(f"Rate limit resets in {wait_time} seconds")
   ```

3. **Implement Exponential Backoff**
   ```python
   import random
   
   def exponential_backoff(attempt, base_delay=1, max_delay=300):
       delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
       time.sleep(delay)
   ```

4. **Batch Operations When Possible**
   ```python
   # Instead of multiple single requests
   for content_id in content_ids:
       get_content(content_id)  # 100 requests
   
   # Use batch endpoints
   get_multiple_content(content_ids)  # 1 request
   ```

### Server-Side Optimization

1. **Use Caching**
   ```python
   # Cache frequently accessed data
   @cache.cached(timeout=300)
   def get_analytics_dashboard():
       return expensive_analytics_calculation()
   ```

2. **Implement Request Queuing**
   ```python
   # Queue non-urgent requests
   if is_rate_limited():
       queue_request_for_later(request)
       return "Request queued for processing"
   ```

3. **Prioritize Critical Operations**
   ```python
   # Different limits for different operations
   if is_critical_operation(request):
       return process_immediately(request)
   else:
       return apply_standard_rate_limit(request)
   ```

## 🔄 Rate Limit Bypass Options

### Burst Credits

Pro and Enterprise users get burst credits:
- **Pro**: 500 burst requests per hour
- **Enterprise**: 2000 burst requests per hour

Burst credits allow temporary exceeding of regular limits for urgent operations.

### Priority Queuing

Enterprise customers can use priority queuing:
```http
X-Priority: high
```

This header ensures requests are processed with higher priority during high load.

### Reserved Capacity

Enterprise customers can reserve API capacity:
- Guaranteed minimum performance
- Isolated resource allocation
- Custom rate limit configurations

## 📊 Monitoring & Analytics

### Rate Limit Metrics Dashboard

Track your usage at: https://dashboard.ainflue.com/api/usage

**Available Metrics:**
- Real-time request count
- Rate limit utilization
- Historical usage patterns
- Endpoint-specific analytics
- Tier comparison and recommendations

### API Usage Alerts

Set up alerts for:
- 80% of rate limit reached
- Frequent 429 responses
- Unusual traffic patterns
- Quota approaching limits

### Usage Analytics API

```bash
GET /analytics/api-usage
{
  "period": "24h",
  "granularity": "hour",
  "metrics": ["requests", "rate_limits", "errors"]
}
```

Response:
```json
{
  "data": {
    "requests": {
      "total": 8500,
      "successful": 8200,
      "rate_limited": 300
    },
    "rate_limits": {
      "hit_percentage": 15.2,
      "most_limited_endpoint": "/content/upload",
      "peak_usage_hour": "14:00-15:00"
    },
    "recommendations": [
      "Consider upgrading to Pro tier",
      "Implement request batching for uploads",
      "Use caching for analytics endpoints"
    ]
  }
}
```

## 🚀 Optimization Strategies

### For Different Use Cases

#### Bulk Content Processing
```python
# Bad: Sequential processing
for file in files:
    upload_content(file)  # Hit rate limits quickly

# Good: Batch processing with delays
batch_size = 10
for i in range(0, len(files), batch_size):
    batch = files[i:i+batch_size]
    process_batch(batch)
    if not is_enterprise_tier():
        time.sleep(calculate_delay())
```

#### Real-time Monitoring
```python
# Use WebSocket for real-time data instead of polling
websocket.connect('wss://api.ainflue.com/v2/events')

# Or implement smart polling with backoff
def smart_poll():
    if has_updates():
        poll_interval = 5  # Fast polling when active
    else:
        poll_interval = 60  # Slow polling when quiet
    
    time.sleep(poll_interval)
```

#### Analytics Dashboards
```python
# Cache expensive analytics calls
@cache.cached(timeout=300)  # 5 minute cache
def get_dashboard_data():
    return api.get('/analytics/dashboard')

# Use delta updates instead of full refreshes
def update_dashboard():
    last_update = get_last_update_time()
    delta = api.get(f'/analytics/delta?since={last_update}')
    apply_delta_updates(delta)
```

## ⚡ Performance Tips

### Request Optimization

1. **Use Compression**
   ```http
   Accept-Encoding: gzip, deflate
   Content-Encoding: gzip
   ```

2. **Optimize Payloads**
   ```json
   // Instead of sending full objects
   {
     "content": {
       "id": "uuid",
       "title": "...",
       "description": "...",
       "metadata": {...}
     }
   }
   
   // Send only required fields
   {
     "title": "...",
     "description": "..."
   }
   ```

3. **Use Conditional Requests**
   ```http
   If-None-Match: "etag-value"
   If-Modified-Since: Tue, 07 Jan 2025 10:00:00 GMT
   ```

### Connection Management

1. **HTTP/2 and Connection Reuse**
   ```python
   import requests
   
   # Use session for connection reuse
   session = requests.Session()
   session.headers.update({'Authorization': 'Bearer token'})
   
   # Multiple requests reuse connection
   response1 = session.get('/api/v2/content/1')
   response2 = session.get('/api/v2/content/2')
   ```

2. **Connection Pooling**
   ```python
   from requests.adapters import HTTPAdapter
   from urllib3.util.retry import Retry
   
   session = requests.Session()
   
   # Configure retry strategy
   retry_strategy = Retry(
       total=3,
       backoff_factor=1,
       status_forcelist=[429, 500, 502, 503, 504]
   )
   
   adapter = HTTPAdapter(
       pool_connections=20,
       pool_maxsize=20,
       max_retries=retry_strategy
   )
   
   session.mount("https://", adapter)
   ```

## 🔧 SDK Rate Limiting

### Python SDK Example

```python
from ainflue_sdk import AinflueFree, AinfluePro
from ainflue_sdk.exceptions import RateLimitExceeded

# SDK automatically handles rate limiting
client = AinfluePro(api_key="your_key")

try:
    # SDK respects rate limits automatically
    content = client.content.upload(file_path)
    
    # SDK provides rate limit info
    print(f"Remaining requests: {client.rate_limit.remaining}")
    print(f"Reset time: {client.rate_limit.reset_time}")
    
except RateLimitExceeded as e:
    print(f"Rate limited. Retry after: {e.retry_after}")
    # SDK can auto-retry with backoff
    content = client.content.upload(file_path, auto_retry=True)
```

### JavaScript SDK Example

```javascript
import { AinflueFree } from '@ainflue/api-sdk';

const client = new AinflueFree({ apiKey: 'your_key' });

// SDK handles rate limiting with promises
try {
  const content = await client.content.upload(fileData, {
    retryOnRateLimit: true,
    maxRetries: 3
  });
  
  // Check rate limit status
  console.log('Rate limit info:', client.rateLimitStatus);
  
} catch (error) {
  if (error.code === 'RATE_LIMIT_EXCEEDED') {
    console.log(`Retry after: ${error.retryAfter} seconds`);
  }
}
```

## 🎯 Tier Comparison & Upgrades

### When to Upgrade

#### From Free to Pro
**Indicators:**
- Hitting 1,000 requests/hour regularly
- Need for more content uploads (>10/day)
- Require more AI processing operations
- Need faster response times

**Benefits:**
- 10x request increase
- 10x content upload increase
- 10x AI processing increase
- Priority support

#### From Pro to Enterprise
**Indicators:**
- Hitting 10,000 requests/hour
- Need for unlimited content uploads
- Require custom integrations
- Need SLA guarantees

**Benefits:**
- 10x request increase
- Unlimited content uploads
- Custom rate limits
- 24/7 support
- Dedicated infrastructure

### Upgrade Process

1. **Contact Sales**: enterprise@ainflue.com
2. **Usage Analysis**: We analyze your current usage patterns
3. **Custom Plan**: Tailored to your specific needs
4. **Migration Support**: Seamless transition assistance
5. **Ongoing Optimization**: Regular performance reviews

## 📞 Support & Troubleshooting

### Common Issues

1. **Unexpected Rate Limiting**
   - Check for concurrent requests from multiple clients
   - Verify API key usage across different applications
   - Monitor for automated scripts or cron jobs

2. **Inconsistent Rate Limit Headers**
   - May indicate load balancer issues
   - Contact support for investigation

3. **Performance Degradation**
   - Check rate limit utilization
   - Consider request optimization
   - Upgrade tier if consistently hitting limits

### Support Channels

- **Rate Limit Issues**: ratelimit-support@ainflue.com
- **Performance Questions**: performance@ainflue.com
- **Tier Upgrades**: sales@ainflue.com
- **Emergency Support**: +1-800-AINFLUE (Enterprise only)

### Debugging Tools

1. **Rate Limit Analyzer**
   ```bash
   curl -H "Authorization: Bearer token" \
        "https://api.ainflue.com/v2/debug/rate-limits"
   ```

2. **Usage Patterns**
   ```bash
   curl -H "Authorization: Bearer token" \
        "https://api.ainflue.com/v2/debug/usage-patterns?period=24h"
   ```

3. **Health Check with Rate Limits**
   ```bash
   curl -H "Authorization: Bearer token" \
        "https://api.ainflue.com/v2/health?include=rate-limits"
   ```

---

## 📋 Rate Limiting Checklist

### Implementation Checklist
- [ ] Monitor rate limit headers in all responses
- [ ] Implement exponential backoff for 429 responses
- [ ] Cache frequently accessed data
- [ ] Use batch operations where available
- [ ] Implement request queuing for non-urgent operations
- [ ] Set up monitoring and alerting for rate limit hits
- [ ] Plan for tier upgrades based on usage growth

### Testing Checklist
- [ ] Test rate limit handling in your application
- [ ] Verify proper error handling for 429 responses
- [ ] Test with different API tiers
- [ ] Validate retry mechanisms
- [ ] Performance test under rate limit conditions

---

**Last Updated**: January 7, 2025  
**Next Review**: April 2025  
**Version**: 2.0