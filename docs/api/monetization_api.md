# Ainflue Monetization API Documentation

## Overview
The Ainflue Monetization API provides comprehensive revenue calculation, payment processing, and distribution capabilities for content creators across multiple platforms.

**Base URL:** `https://api.ainflue.com/v1`  
**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 1.0.0  

## Authentication

All API requests require authentication using JWT tokens.

```http
Authorization: Bearer <your_jwt_token>
```

## Revenue Calculation API

### Calculate Platform Revenue

Calculate revenue for specific platforms with detailed metrics.

**Endpoint:** `POST /monetization/revenue/calculate`

**Request Body:**
```json
{
  "content_id": "string",
  "platform_data": {
    "youtube": {
      "views": 50000,
      "watch_time_hours": 25000,
      "engagement_rate": 0.06,
      "subscriber_count": 5000,
      "country": "US"
    },
    "spotify": {
      "streams": 100000,
      "premium_streams": 60000,
      "country_distribution": {
        "US": 50000,
        "DE": 30000,
        "GB": 20000
      }
    },
    "instagram": {
      "impressions": 200000,
      "reach": 150000,
      "engagement_rate": 0.04,
      "story_views": 25000,
      "follower_count": 3000
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "content_id": "string",
    "revenues": {
      "youtube": 125.50,
      "spotify": 210.00,
      "instagram": 85.30,
      "total": 420.80
    },
    "currency": "EUR",
    "calculated_at": "2025-01-15T10:30:00Z"
  }
}
```

### Get Revenue Predictions

Generate ML-based revenue predictions for future periods.

**Endpoint:** `POST /monetization/revenue/predict`

**Request Body:**
```json
{
  "platform": "youtube",
  "content_id": "string",
  "forecast_days": 30,
  "historical_period_days": 90
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "platform": "youtube",
    "content_id": "string",
    "predictions": [125.50, 128.30, 131.20, "..."],
    "confidence_score": 0.85,
    "trend": "increasing",
    "generated_at": "2025-01-15T10:30:00Z"
  }
}
```

### Get Real-time Revenue

Retrieve real-time revenue estimates for content.

**Endpoint:** `GET /monetization/revenue/realtime/{content_id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "content_id": "string",
    "current_revenue": {
      "youtube": 12.45,
      "instagram": 8.30,
      "tiktok": 2.15,
      "spotify": 15.60,
      "total": 38.50
    },
    "currency": "EUR",
    "last_updated": "2025-01-15T10:30:00Z"
  }
}
```

## Payment Processing API

### Process License Payment

Process payment for content licensing.

**Endpoint:** `POST /monetization/payments/license`

**Request Body:**
```json
{
  "license_id": "string",
  "payer_id": "string",
  "payee_id": "string",
  "amount": 100.0,
  "currency": "EUR",
  "provider": "stripe",
  "payment_method_id": "pm_xxxxxxxxxx",
  "metadata": {
    "content_type": "audio",
    "usage_type": "commercial",
    "territory": "worldwide"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transaction_id": "txn_xxxxxxxxxx",
    "status": "processing",
    "amount": 100.0,
    "fees": 3.20,
    "net_amount": 96.80,
    "currency": "EUR",
    "provider_transaction_id": "ch_xxxxxxxxxx",
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```

### Distribute Revenue Shares

Automatically distribute revenue among collaborators.

**Endpoint:** `POST /monetization/payments/distribute`

**Request Body:**
```json
{
  "revenue_data": {
    "youtube": 100.0,
    "spotify": 50.0,
    "instagram": 75.0
  },
  "split_rules": {
    "creator_1": 0.6,
    "creator_2": 0.3,
    "platform": 0.1
  },
  "currency": "EUR"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_distributed": 225.0,
    "transactions": [
      {
        "transaction_id": "txn_xxxxxxxxxx",
        "payee_id": "creator_1",
        "amount": 135.0,
        "status": "processing"
      },
      {
        "transaction_id": "txn_yyyyyyyyyy",
        "payee_id": "creator_2",
        "amount": 67.5,
        "status": "processing"
      },
      {
        "transaction_id": "txn_zzzzzzzzzz",
        "payee_id": "platform",
        "amount": 22.5,
        "status": "processing"
      }
    ]
  }
}
```

### Create Escrow Transaction

Create escrow for dispute protection.

**Endpoint:** `POST /monetization/payments/escrow`

**Request Body:**
```json
{
  "payment_id": "txn_xxxxxxxxxx",
  "amount": 100.0,
  "currency": "EUR",
  "release_conditions": ["content_delivered", "no_disputes"],
  "dispute_period_days": 7
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "escrow_id": "escrow_xxxxxxxxxx",
    "payment_id": "txn_xxxxxxxxxx",
    "amount": 100.0,
    "currency": "EUR",
    "status": "active",
    "dispute_deadline": "2025-01-22T10:30:00Z",
    "release_conditions": ["content_delivered", "no_disputes"]
  }
}
```

### Release Escrow Funds

Release funds from escrow after conditions are met.

**Endpoint:** `POST /monetization/payments/escrow/{escrow_id}/release`

**Request Body:**
```json
{
  "release_reason": "content_delivered",
  "evidence": {
    "delivery_confirmation": "conf_xxxxxxxxxx",
    "quality_approval": "approved"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "escrow_id": "escrow_xxxxxxxxxx",
    "status": "released",
    "released_at": "2025-01-15T10:30:00Z",
    "release_reason": "content_delivered"
  }
}
```

## Multi-Currency Support

### Process Multi-Currency Payment

Process payments with automatic currency conversion.

**Endpoint:** `POST /monetization/payments/multi-currency`

**Request Body:**
```json
{
  "amount": 100.0,
  "from_currency": "USD",
  "to_currency": "EUR",
  "payer_id": "string",
  "payee_id": "string",
  "conversion_provider": "wise"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transaction_id": "txn_xxxxxxxxxx",
    "original_amount": 100.0,
    "original_currency": "USD",
    "converted_amount": 85.0,
    "target_currency": "EUR",
    "exchange_rate": 0.85,
    "conversion_fees": 0.90,
    "net_amount": 84.10
  }
}
```

## Dispute Management

### Create Payment Dispute

Initiate a dispute for a payment transaction.

**Endpoint:** `POST /monetization/payments/{transaction_id}/dispute`

**Request Body:**
```json
{
  "dispute_reason": "Content not delivered",
  "evidence": {
    "screenshots": ["evidence1.png", "evidence2.png"],
    "correspondence": ["email_thread.pdf"],
    "contract": ["original_agreement.pdf"]
  },
  "requested_action": "refund"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "dispute_id": "dispute_xxxxxxxxxx",
    "transaction_id": "txn_xxxxxxxxxx",
    "status": "open",
    "dispute_reason": "Content not delivered",
    "created_at": "2025-01-15T10:30:00Z",
    "estimated_resolution_time": "3-5 business days"
  }
}
```

## Tax Reporting

### Generate Tax Report

Generate comprehensive tax reports for users.

**Endpoint:** `GET /monetization/tax/report`

**Query Parameters:**
- `user_id`: User ID for the report
- `year`: Tax year (e.g., 2025)
- `country`: Country code (e.g., "DE", "US", "GB")
- `format`: Report format ("json", "pdf", "csv")

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "user_xxxxxxxxxx",
    "year": 2025,
    "country": "DE",
    "total_income": 12500.00,
    "total_expenses": 2300.00,
    "total_fees": 375.00,
    "net_income": 10125.00,
    "tax_obligations": {
      "taxable_income": 375.56,
      "tax_rate": 0.25,
      "tax_owed": 93.89,
      "threshold": 9744
    },
    "transaction_count": 156,
    "generated_at": "2025-01-15T10:30:00Z"
  }
}
```

## Error Responses

All endpoints follow consistent error response format:

```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_FUNDS",
    "message": "Insufficient funds for this transaction",
    "details": {
      "required_amount": 100.0,
      "available_amount": 75.0,
      "currency": "EUR"
    },
    "request_id": "req_xxxxxxxxxx"
  }
}
```

### Common Error Codes

- `AUTHENTICATION_REQUIRED`: Missing or invalid authentication
- `INSUFFICIENT_PERMISSIONS`: User lacks required permissions
- `INVALID_PAYMENT_METHOD`: Payment method is invalid or expired
- `INSUFFICIENT_FUNDS`: Insufficient funds for transaction
- `TRANSACTION_FAILED`: Payment processing failed
- `DISPUTE_ALREADY_EXISTS`: Dispute already exists for transaction
- `ESCROW_NOT_FOUND`: Escrow transaction not found
- `INVALID_CURRENCY`: Unsupported currency code
- `RATE_LIMIT_EXCEEDED`: API rate limit exceeded

## Rate Limits

- **Standard endpoints**: 1000 requests per hour per user
- **Payment endpoints**: 100 requests per hour per user  
- **Dispute endpoints**: 50 requests per hour per user

Rate limit headers are included in all responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642780800
```

## SDKs and Libraries

Official SDKs are available for:
- JavaScript/Node.js
- Python
- PHP
- Ruby
- Go

## Support

For API support and questions:
- **Email**: mlaiel@live.de
- **Documentation**: https://docs.ainflue.com
- **Status Page**: https://status.ainflue.com

---

**Copyright © 2025 Fahed Mlaiel. All rights reserved.**