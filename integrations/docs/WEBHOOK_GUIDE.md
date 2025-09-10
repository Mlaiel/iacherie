# Webhook Implementation Guide - Enterprise Integration
=====================================================

## Table of Contents
- [Webhook Architecture Overview](#webhook-architecture-overview)
- [Webhook Security Implementation](#webhook-security-implementation)
- [Event Types and Payloads](#event-types-and-payloads)
- [Retry Logic and Error Handling](#retry-logic-and-error-handling)
- [Rate Limiting and Throttling](#rate-limiting-and-throttling)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Testing and Validation](#testing-and-validation)
- [Best Practices](#best-practices)

## Webhook Architecture Overview

### Core Components

The Ainflue webhook system consists of several key components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Event Source  │───▶│ Webhook Manager │───▶│   Destination   │
│   (Platform)    │    │    (Ainflue)    │    │   (External)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Event Storage & │
                       │    Analytics    │
                       └─────────────────┘
```

### Webhook Flow

1. **Event Generation**: Platform events trigger webhook notifications
2. **Event Processing**: Webhook manager processes and validates events
3. **Delivery Attempt**: HTTP POST request sent to configured endpoint
4. **Response Handling**: Success/failure responses are processed
5. **Retry Logic**: Failed deliveries are retried with exponential backoff
6. **Analytics**: Delivery metrics are tracked and reported

## Webhook Security Implementation

### HMAC Signature Verification

All webhook payloads include HMAC-SHA256 signatures for verification:

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    """Verify webhook payload signature"""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(
        f"sha256={expected_signature}",
        signature
    )
```

### Headers and Authentication

Required headers for webhook requests:

```http
POST /your-webhook-endpoint HTTP/1.1
Host: your-domain.com
Content-Type: application/json
X-Ainflue-Signature: sha256=<hmac_signature>
X-Ainflue-Event: <event_type>
X-Ainflue-Delivery: <delivery_id>
X-Ainflue-Timestamp: <unix_timestamp>
User-Agent: Ainflue-Webhook/1.0
```

### IP Allowlisting

Webhook requests originate from these IP ranges:

```
# Production IPs
52.10.123.0/24
54.240.0.0/16
198.51.100.0/24

# Staging IPs
10.0.0.0/8
172.16.0.0/12
```

## Event Types and Payloads

### Content Events

#### content.uploaded
```json
{
  "event": "content.uploaded",
  "timestamp": "2025-01-10T12:00:00Z",
  "data": {
    "content_id": "cont_123456789",
    "user_id": "user_abc123",
    "type": "video",
    "filename": "my_video.mp4",
    "size": 52428800,
    "duration": 180,
    "metadata": {
      "resolution": "1920x1080",
      "bitrate": 5000,
      "codec": "h264"
    },
    "processing_status": "completed",
    "upload_timestamp": "2025-01-10T11:58:00Z"
  }
}
```

#### content.processed
```json
{
  "event": "content.processed",
  "timestamp": "2025-01-10T12:05:00Z",
  "data": {
    "content_id": "cont_123456789",
    "user_id": "user_abc123",
    "processing_results": {
      "ai_analysis": {
        "sentiment": "positive",
        "topics": ["music", "creativity", "innovation"],
        "quality_score": 0.92
      },
      "content_protection": {
        "watermark_applied": true,
        "drm_enabled": true,
        "copyright_check": "passed"
      },
      "optimization": {
        "compressed_size": 31457280,
        "thumbnails_generated": 5,
        "formats_created": ["mp4", "webm", "mov"]
      }
    }
  }
}
```

### User Events

#### user.registered
```json
{
  "event": "user.registered",
  "timestamp": "2025-01-10T10:30:00Z",
  "data": {
    "user_id": "user_def456",
    "email": "creator@example.com",
    "user_type": "content_creator",
    "plan": "premium",
    "registration_source": "organic",
    "profile": {
      "name": "Creative Artist",
      "bio": "Digital content creator",
      "social_links": {
        "instagram": "@creativeartist",
        "youtube": "creativeartist"
      }
    }
  }
}
```

#### user.subscription_changed
```json
{
  "event": "user.subscription_changed",
  "timestamp": "2025-01-10T14:20:00Z",
  "data": {
    "user_id": "user_def456",
    "previous_plan": "basic",
    "new_plan": "premium",
    "change_type": "upgrade",
    "effective_date": "2025-01-10T14:20:00Z",
    "billing_cycle": "monthly",
    "amount": 29.99,
    "currency": "USD"
  }
}
```

### Payment Events

#### payment.completed
```json
{
  "event": "payment.completed",
  "timestamp": "2025-01-10T15:45:00Z",
  "data": {
    "payment_id": "pay_987654321",
    "user_id": "user_abc123",
    "amount": 49.99,
    "currency": "USD",
    "payment_method": "stripe",
    "transaction_id": "txn_stripe_123456",
    "item_type": "subscription",
    "item_id": "sub_premium_monthly",
    "status": "succeeded",
    "fees": {
      "platform_fee": 2.50,
      "payment_processor_fee": 1.75
    }
  }
}
```

### Analytics Events

#### analytics.milestone_reached
```json
{
  "event": "analytics.milestone_reached",
  "timestamp": "2025-01-10T16:00:00Z",
  "data": {
    "user_id": "user_abc123",
    "content_id": "cont_123456789",
    "milestone_type": "views",
    "milestone_value": 10000,
    "current_metrics": {
      "total_views": 10000,
      "likes": 750,
      "shares": 125,
      "comments": 89
    },
    "time_to_milestone": "7 days"
  }
}
```

## Retry Logic and Error Handling

### Retry Strategy

Failed webhook deliveries are retried using exponential backoff:

```
Attempt 1: Immediate
Attempt 2: 5 seconds
Attempt 3: 25 seconds (5^2)
Attempt 4: 125 seconds (5^3)
Attempt 5: 625 seconds (5^4)
Maximum: 3600 seconds (1 hour)
```

### HTTP Status Code Handling

| Status Code | Action | Retry |
|-------------|--------|-------|
| 200-299 | Success, stop retrying | No |
| 400-499 | Client error, stop retrying | No |
| 500-599 | Server error, retry | Yes |
| Timeout | Network error, retry | Yes |

### Error Response Format

```json
{
  "error": {
    "code": "webhook_delivery_failed",
    "message": "Failed to deliver webhook after 5 attempts",
    "details": {
      "webhook_id": "wh_123456789",
      "endpoint": "https://api.example.com/webhooks",
      "attempts": 5,
      "last_error": "Connection timeout after 30 seconds",
      "last_attempt": "2025-01-10T17:30:00Z"
    }
  }
}
```

## Rate Limiting and Throttling

### Default Limits

- **Webhook Deliveries**: 100 requests per minute per endpoint
- **Event Generation**: 1000 events per minute per user
- **Retry Attempts**: 5 maximum attempts per webhook
- **Concurrent Deliveries**: 10 per endpoint

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1641823200
X-RateLimit-Type: webhook_delivery
```

### Throttling Behavior

When rate limits are exceeded:

1. **Queue Management**: Webhooks are queued for later delivery
2. **Backoff Strategy**: Delivery attempts are spaced out
3. **Priority Handling**: Critical events get priority in queue
4. **Notification**: Webhook owners are notified of delays

## Monitoring and Alerting

### Delivery Metrics

Key metrics tracked for webhook deliveries:

```yaml
webhook_metrics:
  delivery_rate:
    description: "Percentage of successful deliveries"
    target: "> 99%"
    
  average_response_time:
    description: "Average response time for webhook endpoints"
    target: "< 5 seconds"
    
  retry_rate:
    description: "Percentage of webhooks requiring retries"
    target: "< 5%"
    
  error_rate:
    description: "Percentage of permanent failures"
    target: "< 1%"
```

### Alerting Thresholds

```yaml
alerts:
  high_error_rate:
    condition: "error_rate > 5%"
    severity: "warning"
    notification: "email, slack"
    
  delivery_failure:
    condition: "delivery_rate < 95%"
    severity: "critical"
    notification: "email, slack, pagerduty"
    
  slow_response:
    condition: "avg_response_time > 10s"
    severity: "warning"
    notification: "slack"
```

### Dashboard Metrics

Real-time webhook dashboard includes:

- **Delivery Success Rate**: Rolling 24-hour success percentage
- **Response Time Distribution**: P50, P95, P99 response times
- **Event Volume**: Events per hour/day/month
- **Endpoint Health**: Status of registered webhook endpoints
- **Error Analysis**: Common error patterns and frequencies

## Testing and Validation

### Webhook Testing Tool

Use the webhook testing endpoint to validate your integration:

```bash
curl -X POST https://api.ainflue.com/webhooks/test \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "https://your-domain.com/webhook",
    "event_type": "content.uploaded",
    "test_data": {
      "content_id": "test_content_123",
      "user_id": "test_user_456"
    }
  }'
```

### Validation Checklist

- [ ] Endpoint returns 200-299 status codes
- [ ] HMAC signature verification implemented
- [ ] Idempotency handling for duplicate events
- [ ] Proper error handling and logging
- [ ] Timeout handling (recommended: 30 seconds)
- [ ] Rate limiting compliance
- [ ] Security headers validation

### Local Testing with ngrok

For local development testing:

```bash
# Install ngrok
npm install -g ngrok

# Expose local server
ngrok http 3000

# Use the HTTPS URL for webhook configuration
https://abc123.ngrok.io/webhook
```

## Best Practices

### Endpoint Implementation

1. **Idempotency**: Handle duplicate events gracefully
2. **Fast Response**: Respond quickly (< 5 seconds) to avoid timeouts
3. **Asynchronous Processing**: Queue heavy processing for later
4. **Graceful Degradation**: Continue operating if webhook fails

### Security Best Practices

1. **Signature Verification**: Always verify HMAC signatures
2. **HTTPS Only**: Only accept webhooks over HTTPS
3. **IP Allowlisting**: Restrict access to known IP ranges
4. **Rate Limiting**: Implement your own rate limiting
5. **Input Validation**: Validate all incoming data

### Error Handling

1. **Structured Logging**: Log webhook events with structured data
2. **Error Categorization**: Categorize errors for better debugging
3. **Monitoring Integration**: Connect to your monitoring system
4. **Alerting**: Set up alerts for critical failures

### Performance Optimization

1. **Database Optimization**: Use efficient queries for webhook data
2. **Caching Strategy**: Cache frequently accessed data
3. **Connection Pooling**: Reuse HTTP connections when possible
4. **Batch Processing**: Process multiple events together when appropriate

### Example Implementation (Node.js)

```javascript
const express = require('express');
const crypto = require('crypto');
const bodyParser = require('body-parser');

const app = express();

// Middleware to capture raw body for signature verification
app.use('/webhook', bodyParser.raw({ type: 'application/json' }));

app.post('/webhook', (req, res) => {
  const signature = req.headers['x-ainflue-signature'];
  const timestamp = req.headers['x-ainflue-timestamp'];
  const eventType = req.headers['x-ainflue-event'];
  
  // Verify signature
  if (!verifySignature(req.body, signature)) {
    return res.status(401).send('Invalid signature');
  }
  
  // Verify timestamp (prevent replay attacks)
  const currentTime = Math.floor(Date.now() / 1000);
  if (Math.abs(currentTime - parseInt(timestamp)) > 300) {
    return res.status(401).send('Request too old');
  }
  
  // Process webhook
  try {
    const payload = JSON.parse(req.body);
    processWebhook(eventType, payload);
    
    res.status(200).send('OK');
  } catch (error) {
    console.error('Webhook processing error:', error);
    res.status(500).send('Processing error');
  }
});

function verifySignature(body, signature) {
  const expectedSignature = crypto
    .createHmac('sha256', process.env.WEBHOOK_SECRET)
    .update(body)
    .digest('hex');
    
  return crypto.timingSafeEqual(
    Buffer.from(`sha256=${expectedSignature}`),
    Buffer.from(signature)
  );
}

function processWebhook(eventType, payload) {
  // Implement idempotency check
  const eventId = payload.id || payload.event_id;
  if (isEventProcessed(eventId)) {
    console.log(`Event ${eventId} already processed`);
    return;
  }
  
  // Queue for asynchronous processing
  queueWebhookEvent(eventType, payload);
  
  // Mark as processed
  markEventProcessed(eventId);
}

app.listen(3000, () => {
  console.log('Webhook server listening on port 3000');
});
```

### Example Implementation (Python/FastAPI)

```python
import hmac
import hashlib
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/webhook")
async def handle_webhook(request: Request):
    # Get headers
    signature = request.headers.get("x-ainflue-signature")
    timestamp = request.headers.get("x-ainflue-timestamp")
    event_type = request.headers.get("x-ainflue-event")
    
    # Get raw body
    body = await request.body()
    
    # Verify signature
    if not verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Verify timestamp
    current_time = int(time.time())
    if abs(current_time - int(timestamp)) > 300:
        raise HTTPException(status_code=401, detail="Request too old")
    
    # Process webhook
    try:
        payload = await request.json()
        await process_webhook(event_type, payload)
        return JSONResponse(content={"status": "success"}, status_code=200)
    except Exception as e:
        print(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Processing error")

def verify_signature(body: bytes, signature: str) -> bool:
    """Verify webhook signature"""
    secret = os.getenv("WEBHOOK_SECRET").encode()
    expected_signature = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected_signature}", signature)

async def process_webhook(event_type: str, payload: dict):
    """Process webhook event"""
    # Implement your webhook processing logic here
    print(f"Processing {event_type} event: {payload}")
```

---

## Support and Documentation

For additional webhook support:

- **API Documentation**: https://docs.ainflue.com/webhooks
- **Support Email**: support@ainflue.com
- **Developer Portal**: https://developers.ainflue.com
- **Status Page**: https://status.ainflue.com

---

**© 2025 Fahed Mlaiel. All rights reserved.**  
**Contact**: mlaiel@live.de  
**Legal**: This documentation is part of the Ainflue platform and is protected by international copyright law.