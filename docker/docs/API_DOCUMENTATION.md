# API Documentation Guide

## Docker Services API Documentation for Ainflue Platform

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 3.0  
**Date:** September 2025

### API Overview

This document provides comprehensive API documentation for all Docker services in the Ainflue platform, including REST APIs, gRPC services, and WebSocket endpoints.

### Core Services APIs

#### 1. API Gateway Service
```yaml
# API Gateway - Port 80/443
Base URL: https://api.ainflue.com
Health Check: GET /health
Metrics: GET /metrics
Documentation: GET /docs
```

**Endpoints:**
```http
# Authentication
POST /auth/login
POST /auth/register
POST /auth/refresh
DELETE /auth/logout

# User Management
GET /users/profile
PUT /users/profile
GET /users/{user_id}

# Content Management
GET /content
POST /content
GET /content/{content_id}
PUT /content/{content_id}
DELETE /content/{content_id}
```

#### 2. Authentication Service
```yaml
# Authentication Service - Port 8001
Base URL: http://auth-service:8001
Health Check: GET /health
```

**API Specification:**
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Ainflue Authentication API",
    "version": "1.0.0"
  },
  "paths": {
    "/auth/validate": {
      "post": {
        "summary": "Validate JWT token",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "token": {"type": "string"}
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Token is valid",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "valid": {"type": "boolean"},
                    "user_id": {"type": "string"},
                    "permissions": {"type": "array"}
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### Audio Processing APIs

#### 1. Audio Processor Service
```yaml
# Audio Processor - Port 8010
Base URL: http://audio-processor:8010
Health Check: GET /health
WebSocket: ws://audio-processor:8010/ws/process
```

**REST API:**
```python
# Python client example
import aiohttp
import asyncio

class AudioProcessorClient:
    def __init__(self, base_url="http://audio-processor:8010"):
        self.base_url = base_url
    
    async def process_audio(self, file_path, options=None):
        """Process audio file with AI enhancement"""
        
        with open(file_path, 'rb') as f:
            form_data = aiohttp.FormData()
            form_data.add_field('file', f, filename='audio.wav')
            if options:
                form_data.add_field('options', json.dumps(options))
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/process", data=form_data) as response:
                return await response.json()
    
    async def get_processing_status(self, job_id):
        """Get processing job status"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/jobs/{job_id}") as response:
                return await response.json()
```

**gRPC API:**
```protobuf
// audio_processor.proto
syntax = "proto3";

package ainflue.audio;

service AudioProcessor {
    rpc ProcessAudio(ProcessAudioRequest) returns (stream ProcessAudioResponse);
    rpc GetJobStatus(JobStatusRequest) returns (JobStatusResponse);
    rpc CancelJob(CancelJobRequest) returns (CancelJobResponse);
}

message ProcessAudioRequest {
    bytes audio_data = 1;
    AudioOptions options = 2;
}

message AudioOptions {
    string format = 1;
    int32 sample_rate = 2;
    bool noise_reduction = 3;
    bool ai_enhancement = 4;
    repeated string effects = 5;
}

message ProcessAudioResponse {
    string job_id = 1;
    ProcessingStatus status = 2;
    bytes processed_audio = 3;
    float progress = 4;
}
```

#### 2. Pitch Corrector Service
```yaml
# Pitch Corrector - Port 8005
Base URL: http://pitch-corrector:8005
Health Check: GET /health
```

**API Endpoints:**
```http
POST /correct-pitch
Content-Type: multipart/form-data

Parameters:
- file: Audio file (WAV, MP3, FLAC)
- pitch_shift: Float (-12.0 to +12.0 semitones)
- auto_tune: Boolean (enable auto-tune)
- key: String (musical key for auto-tune)

Response:
{
  "job_id": "uuid",
  "status": "processing",
  "estimated_time": 30
}

GET /jobs/{job_id}
Response:
{
  "job_id": "uuid",
  "status": "completed",
  "download_url": "/download/{job_id}",
  "processing_time": 25.5
}
```

### Monetization APIs

#### 1. Payment Processor Service
```yaml
# Payment Processor - Port 8020
Base URL: http://payment-processor:8020
Health Check: GET /health
```

**API Documentation:**
```yaml
openapi: 3.0.0
info:
  title: Payment Processor API
  version: 1.0.0
paths:
  /payments:
    post:
      summary: Process payment
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                amount:
                  type: number
                  format: decimal
                currency:
                  type: string
                  enum: [USD, EUR, GBP]
                payment_method:
                  type: string
                  enum: [stripe, paypal, crypto]
                user_id:
                  type: string
              required: [amount, currency, payment_method, user_id]
      responses:
        '200':
          description: Payment processed successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  transaction_id:
                    type: string
                  status:
                    type: string
                    enum: [success, pending, failed]
                  payment_url:
                    type: string
```

#### 2. Revenue Tracker Service
```yaml
# Revenue Tracker - Port 8021
Base URL: http://revenue-tracker:8021
Health Check: GET /health
```

**WebSocket API for Real-time Updates:**
```javascript
// JavaScript client example
const ws = new WebSocket('ws://revenue-tracker:8021/ws/revenue');

ws.onopen = function() {
    // Subscribe to user revenue updates
    ws.send(JSON.stringify({
        action: 'subscribe',
        user_id: 'user123',
        channels: ['earnings', 'payouts']
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Revenue update:', data);
    // {
    //   "type": "earnings_update",
    //   "user_id": "user123",
    //   "amount": 15.50,
    //   "currency": "USD",
    //   "timestamp": "2025-09-10T14:30:00Z"
    // }
};
```

### Protection Services APIs

#### 1. Fingerprinting Engine
```yaml
# Fingerprinting Engine - Port 8030
Base URL: http://fingerprinting-engine:8030
Health Check: GET /health
```

**API Client:**
```python
# fingerprint_client.py
import hashlib
import aiohttp

class FingerprintClient:
    def __init__(self, base_url="http://fingerprinting-engine:8030"):
        self.base_url = base_url
    
    async def create_fingerprint(self, content_data, content_type):
        """Create digital fingerprint for content"""
        
        fingerprint_data = {
            'content_hash': hashlib.sha256(content_data).hexdigest(),
            'content_type': content_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/fingerprint",
                json=fingerprint_data
            ) as response:
                return await response.json()
    
    async def check_similarity(self, fingerprint_id, threshold=0.85):
        """Check for similar content"""
        
        params = {'threshold': threshold}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/fingerprint/{fingerprint_id}/similar",
                params=params
            ) as response:
                return await response.json()
```

#### 2. Copyright Monitor Service
```yaml
# Copyright Monitor - Port 8031
Base URL: http://copyright-monitor:8031
Health Check: GET /health
```

**Webhook API:**
```http
POST /webhooks/violation-detected
Content-Type: application/json

{
  "violation_id": "uuid",
  "content_id": "uuid",
  "platform": "youtube",
  "violation_type": "unauthorized_use",
  "confidence": 0.95,
  "detected_at": "2025-09-10T14:30:00Z",
  "evidence": {
    "url": "https://youtube.com/watch?v=...",
    "thumbnail": "https://img.youtube.com/...",
    "similarity_score": 0.95
  }
}
```

### AI Services APIs

#### 1. ML Inference Engine
```yaml
# ML Inference Engine - Port 8040
Base URL: http://ml-inference:8040
Health Check: GET /health
```

**Batch Processing API:**
```python
# ml_inference_client.py
import asyncio
import aiohttp

class MLInferenceClient:
    def __init__(self, base_url="http://ml-inference:8040"):
        self.base_url = base_url
    
    async def batch_inference(self, model_name, inputs):
        """Run batch inference on multiple inputs"""
        
        request_data = {
            'model': model_name,
            'inputs': inputs,
            'batch_size': len(inputs)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/inference/batch",
                json=request_data
            ) as response:
                return await response.json()
    
    async def stream_inference(self, model_name, input_stream):
        """Stream inference for real-time processing"""
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                f"{self.base_url}/inference/stream"
            ) as ws:
                # Send model configuration
                await ws.send_json({
                    'action': 'configure',
                    'model': model_name
                })
                
                # Stream data
                async for data in input_stream:
                    await ws.send_json({
                        'action': 'process',
                        'data': data
                    })
                    
                    result = await ws.receive_json()
                    yield result
```

### Monitoring and Health APIs

#### 1. Prometheus Metrics
```yaml
# Metrics Endpoints
# All services expose metrics on /metrics endpoint

# Example metrics:
http_requests_total{method="GET",endpoint="/health",status="200"} 1250
http_request_duration_seconds_bucket{method="POST",endpoint="/process",le="0.1"} 856
audio_files_processed_total{format="wav"} 1337
memory_usage_bytes{service="audio-processor"} 2147483648
```

#### 2. Health Check API Standard
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Standard Health Check API",
    "version": "1.0.0"
  },
  "paths": {
    "/health": {
      "get": {
        "summary": "Service health check",
        "responses": {
          "200": {
            "description": "Service is healthy",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "status": {
                      "type": "string",
                      "enum": ["healthy", "unhealthy", "degraded"]
                    },
                    "timestamp": {
                      "type": "string",
                      "format": "date-time"
                    },
                    "version": {
                      "type": "string"
                    },
                    "dependencies": {
                      "type": "object",
                      "additionalProperties": {
                        "type": "object",
                        "properties": {
                          "status": {"type": "string"},
                          "response_time": {"type": "number"}
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### API Client Libraries

#### 1. Python SDK
```python
# ainflue_sdk.py
import aiohttp
import asyncio
from typing import Optional, Dict, Any

class AinfluePlatformSDK:
    def __init__(self, api_key: str, base_url: str = "https://api.ainflue.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    # Audio processing methods
    async def process_audio(self, file_path: str, options: Optional[Dict] = None):
        """Process audio file"""
        with open(file_path, 'rb') as f:
            form_data = aiohttp.FormData()
            form_data.add_field('file', f)
            if options:
                form_data.add_field('options', json.dumps(options))
        
        async with self.session.post(f"{self.base_url}/audio/process", data=form_data) as response:
            return await response.json()
    
    # Protection methods
    async def create_fingerprint(self, content_data: bytes, content_type: str):
        """Create content fingerprint"""
        data = {
            'content_type': content_type,
            'data': content_data.hex()
        }
        async with self.session.post(f"{self.base_url}/protection/fingerprint", json=data) as response:
            return await response.json()
    
    # Monetization methods
    async def process_payment(self, amount: float, currency: str, payment_method: str):
        """Process payment"""
        data = {
            'amount': amount,
            'currency': currency,
            'payment_method': payment_method
        }
        async with self.session.post(f"{self.base_url}/payments", json=data) as response:
            return await response.json()

# Usage example
async def main():
    async with AinfluePlatformSDK('your-api-key') as sdk:
        # Process audio
        result = await sdk.process_audio('audio.wav', {'enhance': True})
        print(f"Processing job: {result['job_id']}")
        
        # Create fingerprint
        with open('content.jpg', 'rb') as f:
            fingerprint = await sdk.create_fingerprint(f.read(), 'image/jpeg')
        print(f"Fingerprint ID: {fingerprint['id']}")

asyncio.run(main())
```

#### 2. JavaScript SDK
```javascript
// ainflue-sdk.js
class AinfluePlatformSDK {
    constructor(apiKey, baseUrl = 'https://api.ainflue.com') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        const response = await fetch(url, config);
        return response.json();
    }

    // Audio processing
    async processAudio(file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('options', JSON.stringify(options));

        return this.request('/audio/process', {
            method: 'POST',
            headers: {}, // Remove Content-Type to let browser set boundary
            body: formData
        });
    }

    // Real-time revenue tracking
    subscribeToRevenue(userId, callback) {
        const ws = new WebSocket(`ws://revenue-tracker:8021/ws/revenue`);
        
        ws.onopen = () => {
            ws.send(JSON.stringify({
                action: 'subscribe',
                user_id: userId,
                channels: ['earnings', 'payouts']
            }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            callback(data);
        };

        return ws;
    }
}

// Usage
const sdk = new AinfluePlatformSDK('your-api-key');

// Process audio file
const fileInput = document.getElementById('audio-file');
fileInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    const result = await sdk.processAudio(file, { enhance: true });
    console.log('Processing started:', result.job_id);
});
```

### API Rate Limiting

All APIs implement rate limiting:

```http
# Rate limit headers
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1630000000
X-RateLimit-Window: 3600

# Rate limit exceeded response
HTTP/1.1 429 Too Many Requests
{
  "error": "Rate limit exceeded",
  "retry_after": 60,
  "limit": 1000,
  "window": 3600
}
```

### API Versioning

All APIs support versioning:

```http
# Version in header
API-Version: v1

# Version in URL
GET /api/v1/audio/process
GET /api/v2/audio/process

# Version in Accept header
Accept: application/vnd.ainflue.v1+json
```

### Error Handling

Standard error response format:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "The provided audio file format is not supported",
    "details": {
      "supported_formats": ["wav", "mp3", "flac"],
      "provided_format": "ogg"
    },
    "timestamp": "2025-09-10T14:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### API Documentation Tools

#### 1. OpenAPI Specification Generation
```python
# Generate OpenAPI specs for all services
import requests
import json

services = [
    'audio-processor:8010',
    'payment-processor:8020',
    'fingerprinting-engine:8030'
]

for service in services:
    try:
        response = requests.get(f"http://{service}/openapi.json")
        spec = response.json()
        
        with open(f"docs/{service.split(':')[0]}-openapi.json", 'w') as f:
            json.dump(spec, f, indent=2)
            
        print(f"Generated OpenAPI spec for {service}")
    except Exception as e:
        print(f"Error generating spec for {service}: {e}")
```

#### 2. Interactive API Documentation
All services provide interactive API documentation at `/docs` endpoint using Swagger UI.