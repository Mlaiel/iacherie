# Ainflue Analytics API Documentation

## Overview
The Ainflue Analytics API provides comprehensive performance tracking, revenue analytics, and business intelligence for content creators and platform administrators.

**Base URL:** `https://api.ainflue.com/v1`  
**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 1.0.0  

## Authentication

All API requests require authentication using JWT tokens.

```http
Authorization: Bearer <your_jwt_token>
```

## Revenue Analytics

### Get Revenue Summary

Retrieve comprehensive revenue summary for a user or content.

**Endpoint:** `GET /analytics/revenue/summary`

**Query Parameters:**
- `user_id`: User ID (optional, defaults to authenticated user)
- `content_id`: Specific content ID (optional)
- `period`: Time period ("7d", "30d", "90d", "1y", "all")
- `platforms`: Comma-separated platform list (optional)
- `currency`: Currency code (default: "EUR")

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "user_xxxxxxxxxx",
    "period": "30d",
    "currency": "EUR",
    "summary": {
      "total_revenue": 2450.75,
      "platform_breakdown": {
        "youtube": 1200.50,
        "spotify": 800.25,
        "instagram": 350.00,
        "tiktok": 100.00
      },
      "growth_rate": 0.15,
      "previous_period_revenue": 2130.65
    },
    "top_performing_content": [
      {
        "content_id": "content_xxxxxxxxxx",
        "title": "Popular Track Name",
        "revenue": 450.00,
        "platforms": ["youtube", "spotify"]
      }
    ]
  }
}
```

### Get Revenue Trends

Analyze revenue trends over time with granular data.

**Endpoint:** `GET /analytics/revenue/trends`

**Query Parameters:**
- `user_id`: User ID (optional)
- `content_id`: Content ID (optional)
- `start_date`: Start date (ISO 8601)
- `end_date`: End date (ISO 8601)
- `granularity`: Data granularity ("hour", "day", "week", "month")
- `platforms`: Platforms to include

**Response:**
```json
{
  "success": true,
  "data": {
    "period": {
      "start_date": "2025-01-01T00:00:00Z",
      "end_date": "2025-01-31T23:59:59Z",
      "granularity": "day"
    },
    "trends": [
      {
        "date": "2025-01-01",
        "total_revenue": 85.50,
        "platform_revenue": {
          "youtube": 45.25,
          "spotify": 25.75,
          "instagram": 14.50
        },
        "view_count": 12500,
        "engagement_rate": 0.06
      }
    ],
    "statistics": {
      "avg_daily_revenue": 79.05,
      "peak_revenue_day": "2025-01-15",
      "growth_trend": "increasing",
      "volatility_score": 0.23
    }
  }
}
```

### Revenue Forecasting

Get AI-powered revenue forecasts and predictions.

**Endpoint:** `POST /analytics/revenue/forecast`

**Request Body:**
```json
{
  "user_id": "user_xxxxxxxxxx",
  "forecast_period_days": 90,
  "confidence_level": 0.95,
  "include_seasonality": true,
  "platforms": ["youtube", "spotify", "instagram"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "user_xxxxxxxxxx",
    "forecast_period_days": 90,
    "confidence_level": 0.95,
    "forecasts": [
      {
        "date": "2025-02-01",
        "predicted_revenue": 125.50,
        "confidence_interval": {
          "lower": 110.25,
          "upper": 140.75
        },
        "platform_breakdown": {
          "youtube": 75.30,
          "spotify": 35.20,
          "instagram": 15.00
        }
      }
    ],
    "model_metrics": {
      "accuracy_score": 0.87,
      "model_type": "LSTM",
      "training_period_days": 365,
      "last_updated": "2025-01-15T10:00:00Z"
    }
  }
}
```

## Performance Analytics

### Get Content Performance

Analyze individual content performance across platforms.

**Endpoint:** `GET /analytics/performance/content/{content_id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "content_id": "content_xxxxxxxxxx",
    "title": "Sample Content Title",
    "total_performance": {
      "total_views": 125000,
      "total_revenue": 450.75,
      "avg_engagement_rate": 0.058,
      "platforms_count": 4
    },
    "platform_performance": {
      "youtube": {
        "views": 75000,
        "watch_time_hours": 3750,
        "revenue": 275.50,
        "engagement_rate": 0.062,
        "subscriber_growth": 145
      },
      "spotify": {
        "streams": 35000,
        "revenue": 105.00,
        "saves": 2100,
        "playlist_adds": 850
      },
      "instagram": {
        "impressions": 15000,
        "reach": 12000,
        "revenue": 45.25,
        "engagement_rate": 0.048,
        "story_views": 3500
      }
    },
    "audience_demographics": {
      "age_groups": {
        "18-24": 0.35,
        "25-34": 0.40,
        "35-44": 0.20,
        "45+": 0.05
      },
      "geographic_distribution": {
        "US": 0.45,
        "DE": 0.20,
        "GB": 0.15,
        "CA": 0.10,
        "others": 0.10
      }
    }
  }
}
```

### Platform Comparison

Compare performance across different platforms.

**Endpoint:** `GET /analytics/performance/compare`

**Query Parameters:**
- `user_id`: User ID
- `platforms`: Platforms to compare
- `period`: Time period
- `metrics`: Metrics to compare ("revenue", "engagement", "reach", "all")

**Response:**
```json
{
  "success": true,
  "data": {
    "comparison_period": "30d",
    "platforms": ["youtube", "spotify", "instagram", "tiktok"],
    "metrics": {
      "revenue": {
        "youtube": {
          "value": 1200.50,
          "rank": 1,
          "growth": 0.15,
          "share": 0.49
        },
        "spotify": {
          "value": 800.25,
          "rank": 2,
          "growth": 0.08,
          "share": 0.33
        },
        "instagram": {
          "value": 350.00,
          "rank": 3,
          "growth": 0.22,
          "share": 0.14
        },
        "tiktok": {
          "value": 100.00,
          "rank": 4,
          "growth": 0.45,
          "share": 0.04
        }
      },
      "engagement_rate": {
        "tiktok": 0.08,
        "instagram": 0.06,
        "youtube": 0.055,
        "spotify": 0.04
      },
      "audience_reach": {
        "youtube": 875000,
        "instagram": 450000,
        "tiktok": 320000,
        "spotify": 125000
      }
    },
    "insights": [
      "YouTube generates the highest revenue but TikTok shows highest growth",
      "Instagram has strongest engagement despite lower reach",
      "Spotify shows consistent performance with steady growth"
    ]
  }
}
```

## Audience Analytics

### Get Audience Demographics

Detailed audience demographic analysis.

**Endpoint:** `GET /analytics/audience/demographics`

**Query Parameters:**
- `user_id`: User ID
- `content_id`: Content ID (optional)
- `platform`: Platform filter (optional)
- `period`: Analysis period

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "user_xxxxxxxxxx",
    "period": "30d",
    "total_audience": 125000,
    "demographics": {
      "age_distribution": {
        "13-17": 0.08,
        "18-24": 0.35,
        "25-34": 0.40,
        "35-44": 0.15,
        "45-54": 0.02
      },
      "gender_distribution": {
        "male": 0.52,
        "female": 0.46,
        "other": 0.02
      },
      "geographic_distribution": {
        "countries": {
          "US": 0.35,
          "DE": 0.20,
          "GB": 0.12,
          "CA": 0.08,
          "FR": 0.07,
          "AU": 0.05,
          "others": 0.13
        },
        "regions": {
          "north_america": 0.43,
          "europe": 0.44,
          "asia_pacific": 0.08,
          "others": 0.05
        }
      },
      "device_types": {
        "mobile": 0.68,
        "desktop": 0.25,
        "tablet": 0.07
      },
      "interests": [
        {"category": "music", "affinity": 0.89},
        {"category": "entertainment", "affinity": 0.76},
        {"category": "technology", "affinity": 0.45},
        {"category": "lifestyle", "affinity": 0.38}
      ]
    }
  }
}
```

### Audience Growth Analysis

Track audience growth and retention metrics.

**Endpoint:** `GET /analytics/audience/growth`

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "user_xxxxxxxxxx",
    "period": "90d",
    "growth_metrics": {
      "total_followers": 125000,
      "new_followers": 15000,
      "unfollowers": 3500,
      "net_growth": 11500,
      "growth_rate": 0.102,
      "churn_rate": 0.028
    },
    "platform_growth": {
      "youtube": {
        "subscribers": 85000,
        "growth": 8500,
        "growth_rate": 0.11
      },
      "instagram": {
        "followers": 25000,
        "growth": 2000,
        "growth_rate": 0.087
      },
      "tiktok": {
        "followers": 15000,
        "growth": 1000,
        "growth_rate": 0.071
      }
    },
    "retention_analysis": {
      "30_day_retention": 0.75,
      "60_day_retention": 0.68,
      "90_day_retention": 0.62
    }
  }
}
```

## Business Intelligence

### Get Dashboard Data

Comprehensive dashboard data for business intelligence.

**Endpoint:** `GET /analytics/dashboard`

**Query Parameters:**
- `user_id`: User ID
- `dashboard_type`: Type ("creator", "admin", "business")
- `period`: Time period

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "user_xxxxxxxxxx",
    "dashboard_type": "creator",
    "period": "30d",
    "kpis": {
      "total_revenue": 2450.75,
      "revenue_growth": 0.15,
      "total_views": 875000,
      "engagement_rate": 0.058,
      "new_followers": 11500,
      "content_pieces": 24
    },
    "charts": {
      "revenue_over_time": {
        "type": "line",
        "data": [/* time series data */],
        "currency": "EUR"
      },
      "platform_revenue_pie": {
        "type": "pie",
        "data": {
          "youtube": 1200.50,
          "spotify": 800.25,
          "instagram": 350.00
        }
      },
      "audience_growth": {
        "type": "area",
        "data": [/* growth data */]
      }
    },
    "alerts": [
      {
        "type": "revenue_drop",
        "message": "Revenue decreased by 15% compared to last week",
        "severity": "warning",
        "platform": "instagram"
      }
    ],
    "recommendations": [
      {
        "type": "content_optimization",
        "message": "Upload frequency on YouTube could be increased for better revenue",
        "impact": "high",
        "effort": "medium"
      }
    ]
  }
}
```

### Export Analytics Data

Export analytics data in various formats.

**Endpoint:** `POST /analytics/export`

**Request Body:**
```json
{
  "user_id": "user_xxxxxxxxxx",
  "export_type": "comprehensive",
  "format": "csv",
  "period": "1y",
  "include_segments": ["revenue", "audience", "performance"],
  "email_delivery": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "export_id": "export_xxxxxxxxxx",
    "status": "processing",
    "estimated_completion": "2025-01-15T11:00:00Z",
    "download_url": null,
    "file_size_mb": null,
    "email_notification": true
  }
}
```

### Custom Reports

Create and retrieve custom analytics reports.

**Endpoint:** `POST /analytics/reports/custom`

**Request Body:**
```json
{
  "report_name": "Q1 Performance Review",
  "user_id": "user_xxxxxxxxxx",
  "date_range": {
    "start": "2025-01-01",
    "end": "2025-03-31"
  },
  "metrics": [
    "total_revenue",
    "platform_breakdown",
    "audience_growth",
    "engagement_trends"
  ],
  "filters": {
    "platforms": ["youtube", "spotify"],
    "content_types": ["music", "video"]
  },
  "visualization_preferences": {
    "include_charts": true,
    "chart_types": ["line", "bar", "pie"],
    "color_scheme": "brand"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "report_id": "report_xxxxxxxxxx",
    "report_name": "Q1 Performance Review",
    "status": "generating",
    "estimated_completion": "2025-01-15T11:15:00Z",
    "format": "pdf",
    "scheduled_delivery": null
  }
}
```

## Real-time Analytics

### Get Live Statistics

Retrieve real-time performance statistics.

**Endpoint:** `GET /analytics/live/stats`

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "user_xxxxxxxxxx",
    "live_stats": {
      "current_viewers": 2450,
      "revenue_today": 125.75,
      "new_followers_today": 45,
      "engagement_rate_1h": 0.067,
      "trending_content": [
        {
          "content_id": "content_xxxxxxxxxx",
          "title": "Trending Track",
          "current_views": 12500,
          "velocity": 0.85
        }
      ]
    },
    "platform_activity": {
      "youtube": {
        "live_viewers": 1500,
        "revenue_today": 75.50
      },
      "spotify": {
        "current_streams": 850,
        "revenue_today": 35.25
      },
      "instagram": {
        "story_viewers": 100,
        "revenue_today": 15.00
      }
    },
    "last_updated": "2025-01-15T10:30:00Z"
  }
}
```

## Webhooks

Subscribe to real-time analytics events via webhooks.

**Supported Events:**
- `revenue.milestone_reached`
- `audience.growth_spike`
- `performance.anomaly_detected`
- `content.viral_detected`

**Webhook Payload Example:**
```json
{
  "event_type": "revenue.milestone_reached",
  "timestamp": "2025-01-15T10:30:00Z",
  "user_id": "user_xxxxxxxxxx",
  "data": {
    "milestone_type": "monthly_revenue",
    "milestone_value": 1000.0,
    "currency": "EUR",
    "achievement_date": "2025-01-15T10:30:00Z"
  }
}
```

---

**Copyright © 2025 Fahed Mlaiel. All rights reserved.**