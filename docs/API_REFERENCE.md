# 📚 API REFERENCE - DISTRIBUTION MODULE

**Version:** 3.0  
**Date:** Décembre 2024  
**Author:** Fahed Mlaiel (mlaiel@live.de)

---

## 🎯 OVERVIEW

Cette référence API complète couvre tous les endpoints et méthodes du module Distribution d'Ainflue, incluant les 8 modules principaux avec leurs interfaces IA avancées.

## 🔗 BASE CONFIGURATION

### 🌐 Base URLs
```
Production:  https://api.ainflue.com/v1/distribution/
Staging:     https://staging-api.ainflue.com/v1/distribution/
Development: http://localhost:8000/v1/distribution/
```

### 🔑 Authentication
```http
Authorization: Bearer <JWT_TOKEN>
X-API-Key: <API_KEY>
Content-Type: application/json
```

---

## 🚀 VIRAL OPTIMIZATION API

### **POST** `/viral/predict`
Prédiction potentiel viral avec IA avancée

#### Request
```json
{
  "content_id": "string",
  "content_type": "video|image|audio|text",
  "metadata": {
    "title": "string",
    "description": "string", 
    "tags": ["string"],
    "duration": "number",
    "file_size": "number"
  },
  "target_platforms": ["instagram", "tiktok", "youtube"],
  "analysis_depth": "quick|detailed|comprehensive"
}
```

#### Response
```json
{
  "viral_score": 0.94,
  "confidence": 0.89,
  "prediction_factors": {
    "content_quality": 0.92,
    "timing_score": 0.88,
    "trend_alignment": 0.96,
    "audience_match": 0.91
  },
  "optimization_suggestions": [
    {
      "type": "timing",
      "suggestion": "Post between 18:00-20:00 for maximum engagement",
      "impact_score": 0.15
    }
  ],
  "expected_metrics": {
    "views": {"min": 10000, "max": 50000, "median": 25000},
    "engagement_rate": {"min": 0.08, "max": 0.15, "median": 0.12}
  }
}
```

### **POST** `/viral/optimize`
Optimisation contenu pour viralité

#### Request
```json
{
  "content_id": "string",
  "optimization_goals": ["reach", "engagement", "conversion"],
  "target_audience": {
    "demographics": {
      "age_range": [18, 35],
      "gender": "all|male|female",
      "locations": ["US", "UK", "CA"]
    },
    "interests": ["music", "technology", "fashion"]
  },
  "platforms": ["instagram", "tiktok", "youtube"]
}
```

#### Response
```json
{
  "optimized_content": {
    "title_suggestions": ["string"],
    "description_optimized": "string",
    "hashtag_recommendations": ["#viral", "#trending"],
    "timing_recommendations": {
      "instagram": "2024-01-15T18:30:00Z",
      "tiktok": "2024-01-15T19:00:00Z"
    }
  },
  "expected_improvement": {
    "reach_increase": 0.45,
    "engagement_boost": 0.32
  }
}
```

---

## 🧠 AUDIENCE INTELLIGENCE API

### **GET** `/audience/profile/{user_id}`
Profil audience détaillé IA

#### Response
```json
{
  "user_id": "string",
  "demographics": {
    "age_distribution": {"18-24": 0.3, "25-34": 0.45, "35-44": 0.25},
    "gender_split": {"male": 0.52, "female": 0.48},
    "top_locations": [
      {"country": "US", "percentage": 0.4},
      {"country": "UK", "percentage": 0.2}
    ]
  },
  "psychographics": {
    "personality_traits": {
      "openness": 0.78,
      "conscientiousness": 0.65,
      "extraversion": 0.82
    },
    "values": ["creativity", "authenticity", "innovation"],
    "lifestyle_segments": ["early_adopters", "content_creators"]
  },
  "engagement_patterns": {
    "peak_activity_hours": [18, 19, 20],
    "preferred_content_types": ["video", "image", "audio"],
    "interaction_frequency": "high",
    "loyalty_score": 0.87
  },
  "predictions": {
    "next_engagement_probability": 0.73,
    "content_preferences": ["behind_scenes", "tutorials", "entertainment"],
    "optimal_posting_frequency": "3-4 posts/week"
  }
}
```

### **POST** `/audience/analyze`
Analyse comportement audience temps réel

#### Request
```json
{
  "content_id": "string",
  "analysis_period": "1h|6h|24h|7d",
  "metrics_to_analyze": ["engagement", "reach", "saves", "shares"]
}
```

#### Response
```json
{
  "analysis_results": {
    "engagement_trends": {
      "current_rate": 0.125,
      "trend_direction": "increasing",
      "trend_strength": 0.85
    },
    "audience_segments": [
      {
        "segment_name": "highly_engaged",
        "size": 15000,
        "characteristics": ["frequent_commenters", "early_interactors"]
      }
    ],
    "behavioral_insights": [
      {
        "insight": "Audience responds 40% better to video content",
        "confidence": 0.92,
        "recommendation": "Increase video content ratio"
      }
    ]
  }
}
```

---

## 📈 CONTENT AMPLIFICATION API

### **POST** `/amplification/strategy`
Stratégie amplification intelligente

#### Request
```json
{
  "content_id": "string",
  "amplification_goals": {
    "target_reach": 100000,
    "target_engagement_rate": 0.12,
    "budget_limit": 500.00
  },
  "available_channels": {
    "organic": ["cross_posting", "community_sharing"],
    "paid": ["instagram_ads", "facebook_ads", "google_ads"],
    "partnerships": ["influencer_collaborations", "brand_partnerships"]
  }
}
```

#### Response
```json
{
  "amplification_strategy": {
    "strategy_id": "string",
    "total_estimated_reach": 125000,
    "estimated_cost": 450.00,
    "roi_prediction": 3.2,
    "execution_timeline": "72 hours",
    "channels": [
      {
        "channel": "instagram_cross_posting",
        "type": "organic",
        "estimated_reach": 25000,
        "cost": 0,
        "execution_time": "immediate"
      },
      {
        "channel": "instagram_ads",
        "type": "paid",
        "estimated_reach": 75000,
        "cost": 300.00,
        "targeting": {
          "demographics": {"age": [18, 35]},
          "interests": ["music", "entertainment"]
        }
      }
    ]
  },
  "performance_predictions": {
    "week_1": {"reach": 50000, "engagement": 6000},
    "week_2": {"reach": 75000, "engagement": 9000}
  }
}
```

### **POST** `/amplification/execute`
Exécution stratégie amplification

#### Request
```json
{
  "strategy_id": "string",
  "execution_options": {
    "start_immediately": true,
    "schedule_start": "2024-01-15T18:00:00Z",
    "auto_optimize": true,
    "max_budget": 500.00
  }
}
```

#### Response
```json
{
  "execution_id": "string",
  "status": "started|scheduled|completed|failed",
  "live_metrics": {
    "current_reach": 1250,
    "current_engagement": 156,
    "spent_budget": 12.50,
    "roi_current": 2.8
  },
  "next_optimization": "2024-01-15T19:00:00Z"
}
```

---

## 🎯 PLATFORM OPTIMIZATION API

### **GET** `/platform/analysis/{platform}`
Analyse spécifique plateforme

#### Response
```json
{
  "platform": "instagram",
  "algorithm_insights": {
    "current_version": "v2.1.3",
    "key_factors": [
      {"factor": "engagement_velocity", "weight": 0.35},
      {"factor": "content_relevance", "weight": 0.28},
      {"factor": "user_relationships", "weight": 0.22}
    ],
    "recent_changes": [
      {
        "date": "2024-01-10",
        "change": "Increased weight for video content",
        "impact": "15% boost for video posts"
      }
    ]
  },
  "optimization_recommendations": [
    {
      "recommendation": "Post Reels during peak hours (18-20h)",
      "expected_boost": 0.25,
      "confidence": 0.89
    }
  ],
  "performance_benchmarks": {
    "top_10_percent": {"engagement_rate": 0.18, "reach_rate": 0.45},
    "median": {"engagement_rate": 0.08, "reach_rate": 0.12}
  }
}
```

### **POST** `/platform/optimize`
Optimisation contenu pour plateforme spécifique

#### Request
```json
{
  "content_id": "string",
  "platform": "instagram",
  "content_type": "reel|post|story|igtv",
  "optimization_level": "basic|advanced|premium"
}
```

#### Response
```json
{
  "optimized_content": {
    "format_adjustments": {
      "aspect_ratio": "9:16",
      "duration": "15-30 seconds",
      "resolution": "1080x1920"
    },
    "caption_optimization": {
      "recommended_length": "125-150 characters",
      "hook_suggestions": ["string"],
      "cta_recommendations": ["string"]
    },
    "hashtag_strategy": {
      "trending_hashtags": ["#trending1", "#viral2"],
      "niche_hashtags": ["#specific1", "#targeted2"],
      "total_recommended": 12
    },
    "posting_strategy": {
      "optimal_time": "2024-01-15T19:30:00Z",
      "frequency_recommendation": "1 Reel/day",
      "cross_posting_suggestions": ["tiktok", "youtube_shorts"]
    }
  }
}
```

---

## 🌍 GEOGRAPHIC OPTIMIZATION API

### **POST** `/geo/targeting`
Ciblage géographique intelligent

#### Request
```json
{
  "content_id": "string",
  "target_regions": ["US", "UK", "CA", "AU"],
  "cultural_adaptation": true,
  "localization_level": "basic|advanced|native"
}
```

#### Response
```json
{
  "geographic_strategy": {
    "region_priorities": [
      {
        "region": "US",
        "priority_score": 0.95,
        "market_potential": "very_high",
        "competition_level": "high",
        "recommended_budget_allocation": 0.4
      }
    ],
    "cultural_adaptations": {
      "US": {
        "language_adjustments": ["American English spelling"],
        "cultural_references": ["local events", "holidays"],
        "visual_preferences": ["bright colors", "dynamic movements"]
      }
    },
    "timing_optimizations": {
      "US": {"optimal_times": ["18:00-20:00 EST"]},
      "UK": {"optimal_times": ["19:00-21:00 GMT"]}
    }
  }
}
```

### **GET** `/geo/compliance/{country}`
Vérification conformité par pays

#### Response
```json
{
  "country": "DE",
  "compliance_status": "compliant|warning|non_compliant",
  "requirements": {
    "data_protection": {
      "gdpr_compliant": true,
      "cookie_consent_required": true,
      "data_localization": false
    },
    "content_regulations": {
      "age_restrictions": ["18+ content must be marked"],
      "advertising_rules": ["clear ad disclosure required"],
      "prohibited_content": ["gambling", "tobacco"]
    }
  },
  "recommendations": [
    {
      "type": "legal",
      "recommendation": "Add GDPR consent banner",
      "priority": "high"
    }
  ]
}
```

---

## ⚡ REAL-TIME OPTIMIZATION API

### **GET** `/realtime/metrics/{content_id}`
Métriques temps réel

#### Response
```json
{
  "content_id": "string",
  "live_metrics": {
    "current_views": 15420,
    "engagement_rate": 0.125,
    "reach": 12500,
    "impressions": 18750,
    "saves": 890,
    "shares": 234,
    "comments": 456,
    "likes": 1854
  },
  "trending_status": {
    "is_trending": true,
    "trending_score": 0.87,
    "trending_in_regions": ["US", "UK"],
    "trend_velocity": "accelerating"
  },
  "real_time_insights": [
    {
      "insight": "Engagement velocity 40% above average",
      "timestamp": "2024-01-15T18:45:32Z",
      "confidence": 0.94
    }
  ],
  "next_update": "2024-01-15T18:50:00Z"
}
```

### **POST** `/realtime/optimize`
Optimisation adaptative temps réel

#### Request
```json
{
  "content_id": "string",
  "optimization_triggers": {
    "engagement_threshold": 0.10,
    "reach_target": 50000,
    "time_window": "6h"
  },
  "auto_actions": {
    "boost_budget": 100.00,
    "cross_post": true,
    "notify_collaborators": true
  }
}
```

#### Response
```json
{
  "optimization_activated": true,
  "actions_taken": [
    {
      "action": "increased_promotion_budget",
      "amount": 50.00,
      "expected_reach_boost": 15000,
      "timestamp": "2024-01-15T18:47:00Z"
    }
  ],
  "performance_prediction": {
    "next_hour_estimates": {
      "views": 25000,
      "engagement": 3125
    }
  }
}
```

---

## 🤝 COLLABORATION API

### **POST** `/collaboration/match`
Matching créateurs IA

#### Request
```json
{
  "creator_id": "string",
  "collaboration_type": "duet|collab|cross_promotion|brand_deal",
  "matching_criteria": {
    "audience_overlap": {"min": 0.2, "max": 0.7},
    "follower_count_range": {"min": 10000, "max": 100000},
    "engagement_rate": {"min": 0.08},
    "content_style": ["similar", "complementary"],
    "niches": ["music", "lifestyle", "tech"]
  },
  "budget_range": {"min": 0, "max": 5000}
}
```

#### Response
```json
{
  "matches": [
    {
      "creator_id": "string",
      "username": "string",
      "match_score": 0.89,
      "compatibility_factors": {
        "audience_overlap": 0.35,
        "content_synergy": 0.92,
        "engagement_compatibility": 0.87,
        "brand_alignment": 0.94
      },
      "collaboration_potential": {
        "estimated_reach": 150000,
        "expected_engagement_boost": 0.25,
        "success_probability": 0.78
      },
      "suggested_collaboration_types": ["duet", "cross_promotion"],
      "estimated_cost": {"min": 500, "max": 1500}
    }
  ],
  "matching_insights": [
    {
      "insight": "High audience synergy with music creators",
      "confidence": 0.91
    }
  ]
}
```

### **POST** `/collaboration/campaign`
Création campagne collaborative

#### Request
```json
{
  "campaign_name": "string",
  "creators": ["creator_id_1", "creator_id_2"],
  "campaign_type": "synchronized_post|sequential_release|joint_content",
  "timeline": {
    "start_date": "2024-01-20T00:00:00Z",
    "end_date": "2024-01-27T23:59:59Z",
    "milestones": [
      {
        "date": "2024-01-22T18:00:00Z",
        "action": "simultaneous_posting"
      }
    ]
  },
  "budget": 2000.00
}
```

#### Response
```json
{
  "campaign_id": "string",
  "status": "created",
  "campaign_predictions": {
    "total_estimated_reach": 300000,
    "expected_engagement": 36000,
    "roi_prediction": 4.2,
    "viral_probability": 0.65
  },
  "execution_plan": [
    {
      "phase": "preparation",
      "duration": "3 days",
      "tasks": ["content_creation", "approval_process"]
    }
  ]
}
```

---

## 🚨 CRISIS MANAGEMENT API

### **GET** `/crisis/monitor/{content_id}`
Monitoring crises temps réel

#### Response
```json
{
  "content_id": "string",
  "crisis_level": "none|low|medium|high|critical",
  "risk_score": 0.23,
  "detected_issues": [
    {
      "type": "negative_sentiment_spike",
      "severity": "medium", 
      "confidence": 0.87,
      "detected_at": "2024-01-15T18:30:00Z",
      "description": "Negative comments increased by 150% in last hour"
    }
  ],
  "sentiment_analysis": {
    "overall_sentiment": 0.65,
    "sentiment_trend": "declining",
    "positive_ratio": 0.72,
    "negative_ratio": 0.28
  },
  "recommendations": [
    {
      "priority": "high",
      "action": "monitor_closely",
      "reason": "Sentiment declining rapidly"
    }
  ]
}
```

### **POST** `/crisis/response`
Activation réponse crise

#### Request
```json
{
  "content_id": "string",
  "crisis_type": "negative_feedback|controversy|platform_violation|legal_issue",
  "response_level": "monitor|moderate|aggressive|emergency",
  "auto_actions": {
    "pause_promotion": true,
    "limit_visibility": false,
    "notify_team": true
  }
}
```

#### Response
```json
{
  "response_activated": true,
  "actions_executed": [
    {
      "action": "promotion_paused",
      "timestamp": "2024-01-15T18:45:00Z",
      "affected_budget": 150.00
    },
    {
      "action": "team_notified",
      "notification_channels": ["email", "slack", "sms"]
    }
  ],
  "damage_control_plan": {
    "estimated_impact_reduction": 0.65,
    "recovery_timeline": "24-48 hours",
    "recommended_follow_up": [
      "Address concerns in public response",
      "Monitor sentiment for 72 hours"
    ]
  }
}
```

---

## 📊 ANALYTICS & REPORTING API

### **GET** `/analytics/performance/{content_id}`
Analytics performance complètes

#### Response
```json
{
  "content_id": "string",
  "time_period": "24h",
  "metrics": {
    "reach": {
      "total": 125000,
      "organic": 85000,
      "paid": 40000,
      "growth_rate": 0.25
    },
    "engagement": {
      "total_interactions": 15600,
      "engagement_rate": 0.125,
      "likes": 12000,
      "comments": 1200,
      "shares": 2400
    },
    "conversions": {
      "profile_visits": 5400,
      "link_clicks": 890,
      "follows": 234,
      "conversion_rate": 0.043
    }
  },
  "platform_breakdown": {
    "instagram": {"reach": 75000, "engagement_rate": 0.14},
    "tiktok": {"reach": 50000, "engagement_rate": 0.18}
  },
  "audience_insights": {
    "demographics": {
      "age_groups": {"18-24": 0.4, "25-34": 0.35},
      "top_countries": ["US", "UK", "CA"]
    },
    "behavior": {
      "peak_engagement_hours": [18, 19, 20],
      "device_usage": {"mobile": 0.85, "desktop": 0.15}
    }
  }
}
```

### **GET** `/analytics/dashboard`
Dashboard analytics global

#### Response
```json
{
  "overview": {
    "total_content_pieces": 1250,
    "total_reach": 15600000,
    "total_engagement": 1950000,
    "average_engagement_rate": 0.125,
    "active_campaigns": 45
  },
  "trends": {
    "reach_trend": "increasing",
    "engagement_trend": "stable",
    "viral_content_count": 23,
    "crisis_incidents": 2
  },
  "top_performing_content": [
    {
      "content_id": "string",
      "title": "string",
      "reach": 250000,
      "engagement_rate": 0.18,
      "viral_score": 0.95
    }
  ],
  "platform_performance": {
    "instagram": {"avg_engagement": 0.12, "reach_growth": 0.15},
    "tiktok": {"avg_engagement": 0.16, "reach_growth": 0.22}
  }
}
```

---

## 🔧 UTILITY ENDPOINTS

### **GET** `/health`
Santé système

#### Response
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "timestamp": "2024-01-15T18:50:00Z",
  "services": {
    "viral_optimization": "operational",
    "audience_intelligence": "operational", 
    "real_time_monitoring": "operational",
    "platform_apis": "operational"
  },
  "performance": {
    "avg_response_time": "45ms",
    "uptime": "99.99%",
    "error_rate": "0.01%"
  }
}
```

### **GET** `/limits`
Limites et quotas

#### Response
```json
{
  "rate_limits": {
    "predictions_per_hour": 1000,
    "distributions_per_day": 10000,
    "api_calls_per_minute": 100
  },
  "current_usage": {
    "predictions_used": 245,
    "distributions_used": 1250,
    "api_calls_used": 25
  },
  "reset_times": {
    "hourly_reset": "2024-01-15T19:00:00Z",
    "daily_reset": "2024-01-16T00:00:00Z"
  }
}
```

---

## 🚨 ERROR CODES

### Standard HTTP Codes
- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **429**: Rate Limit Exceeded
- **500**: Internal Server Error

### Custom Error Codes
```json
{
  "error": {
    "code": "VIRAL_PREDICTION_FAILED",
    "message": "Unable to generate viral prediction",
    "details": "Insufficient content data for analysis",
    "timestamp": "2024-01-15T18:50:00Z",
    "request_id": "req_123456789"
  }
}
```

### Error Code Reference
- **VIRAL_001**: Viral prediction model unavailable
- **AUDIENCE_002**: Insufficient audience data
- **PLATFORM_003**: Platform API rate limit exceeded
- **GEO_004**: Region not supported
- **COLLAB_005**: No matching creators found
- **CRISIS_006**: Crisis detection system offline

---

## 📝 SDK EXAMPLES

### Python SDK
```python
from ainflue_distribution import DistributionClient

client = DistributionClient(api_key="your_api_key")

# Viral prediction
prediction = await client.viral.predict(
    content_id="content_123",
    platforms=["instagram", "tiktok"]
)

# Collaboration matching
matches = await client.collaboration.match(
    creator_id="creator_456",
    criteria={"engagement_rate": {"min": 0.08}}
)
```

### JavaScript SDK
```javascript
import { DistributionClient } from '@ainflue/distribution-sdk';

const client = new DistributionClient({ apiKey: 'your_api_key' });

// Real-time metrics
const metrics = await client.realtime.getMetrics('content_123');

// Platform optimization
const optimization = await client.platform.optimize({
    contentId: 'content_123',
    platform: 'instagram'
});
```

---

**© 2024 Fahed Mlaiel - API Documentation Distribution**  
**Contact: mlaiel@live.de | Documentation Technique Exclusive**