# IA-Influencer-Agent - Configuration Système 46 Agents

**Auteur :** Fahed Mlaiel <mlaiel@live.de>  
**Version :** 2.0.0 - Configuration Industrielle  
**Date :** 13 Août 2025  

## ⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE

**Cette configuration système est la propriété intellectuelle exclusive de Fahed Mlaiel. Toute utilisation non autorisée est strictement interdite. Contact : mlaiel@live.de**

---

## 🔧 Configuration Templates Agents (46 Agents)

### Analytics Agent Configuration
```yaml
analytics_agent:
  data_warehouse_config:
    host: "localhost"
    port: 5432
    database: "analytics_db"
    username: "analytics_user"
    password: "${ANALYTICS_DB_PASSWORD}"
  
  platform_api_keys:
    spotify: "${SPOTIFY_API_KEY}"
    youtube: "${YOUTUBE_API_KEY}"
    instagram: "${INSTAGRAM_API_KEY}"
    tiktok: "${TIKTOK_API_KEY}"
    twitter: "${TWITTER_API_KEY}"
  
  ml_model_config:
    forecasting_model: "prophet"
    anomaly_detection_sensitivity: 0.95
    trend_analysis_window_days: 90
  
  real_time_processing:
    enabled: true
    batch_size: 1000
    processing_interval_seconds: 60
```

### Moderation Agent Configuration
```yaml
moderation_agent:
  moderation_thresholds:
    toxicity: 0.7
    hate_speech: 0.6
    nsfw_content: 0.8
    violence: 0.7
  
  model_configs:
    toxicity_model: "detoxify-multilingual"
    nsfw_model: "nudenet"
    hate_speech_model: "toxic-bert"
  
  review_workflow:
    auto_approve_threshold: 0.1
    human_review_threshold: 0.75
    auto_block_threshold: 0.9
  
  compliance_settings:
    gdpr_compliant: true
    audit_logging: true
    retention_days: 90
```

### Recommendation Agent Configuration
```yaml
recommendation_agent:
  recommendation_models:
    collaborative_filtering:
      algorithm: "matrix_factorization"
      factors: 50
      regularization: 0.01
    
    content_based:
      similarity_metric: "cosine"
      feature_extraction: "tfidf"
    
    hybrid:
      cf_weight: 0.6
      content_weight: 0.4
  
  embedding_configs:
    sentence_transformer_model: "all-MiniLM-L6-v2"
    embedding_dimension: 384
    cache_embeddings: true
  
  personalization_settings:
    min_interactions: 5
    decay_factor: 0.95
    novelty_weight: 0.2
  
  ab_testing_config:
    enabled: true
    test_percentage: 10
    metrics_tracking: ["ctr", "conversion", "satisfaction"]
```

### Support Agent Configuration
```yaml
support_agent:
  conversation_model_config:
    model_name: "microsoft/DialoGPT-medium"
    max_response_length: 150
    temperature: 0.7
  
  knowledge_base_config:
    articles_path: "/data/knowledge_base/"
    index_type: "faiss"
    similarity_threshold: 0.7
  
  escalation_rules:
    sentiment_threshold: -0.7
    max_conversation_turns: 10
    auto_escalate_categories: ["billing", "security"]
  
  supported_channels:
    - "chat"
    - "email" 
    - "phone"
    - "video_call"
```

## 🚀 Quick Setup Guide

### 1. Environment Variables
Create a `.env` file with required API keys and secrets:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ia_influencer_db
REDIS_URL=redis://localhost:6379

# API Keys
SPOTIFY_API_KEY=your_spotify_key
YOUTUBE_API_KEY=your_youtube_key
INSTAGRAM_API_KEY=your_instagram_key
TIKTOK_API_KEY=your_tiktok_key
TWITTER_API_KEY=your_twitter_key

# Security
JWT_SECRET_KEY=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key

# Analytics
ANALYTICS_DB_PASSWORD=your_analytics_password

# External Services
OPENAI_API_KEY=your_openai_key
HUGGING_FACE_TOKEN=your_hf_token
```

### 2. Initialize Agent System
```python
from backend.ai_agents import initialize_agent_system, agent_manager

async def startup():
    # Initialize the complete agent system
    success = await initialize_agent_system()
    if success:
        print("✅ AI Agents system initialized successfully")
    else:
        print("❌ Failed to initialize AI Agents system")
```

### 3. Create and Use Agents
```python
from backend.ai_agents import AgentFactory, AgentRequest

# Create an analytics agent
analytics_agent = await AgentFactory.create_agent(
    agent_type="analytics_agent",
    agent_id="analytics_001",
    config={
        "data_warehouse_config": {...},
        "platform_api_keys": {...}
    }
)

# Create a request
request = AgentRequest(
    action="generate_analytics_report",
    data={
        "user_id": "user123",
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-12-31"
        },
        "platforms": ["spotify", "youtube", "instagram"]
    }
)

# Process the request
response = await analytics_agent.process_request(request)
print(f"Response: {response.data}")
```

## 📊 Agent Performance Monitoring

### Health Checks
```python
# Get system status
status = await agent_manager.get_system_status()
print(f"Total agents: {status['total_agents']}")
print(f"Active pools: {status['total_pools']}")

# Get individual agent health
agent_health = await analytics_agent.get_health_status()
print(f"Agent status: {agent_health['status']}")
print(f"Uptime: {agent_health['uptime_seconds']}s")
```

### Metrics Collection
All agents automatically collect:
- Request count and success/failure rates
- Response times and performance metrics
- Resource usage (CPU, memory)
- Error rates and types
- Custom business metrics per agent type

## 🔒 Security & Compliance

### Data Protection
- All sensitive data encrypted at rest and in transit
- GDPR/CCPA compliant data handling
- Audit logging for all agent actions
- Role-based access control (RBAC)

### Rate Limiting
- Per-user and per-agent rate limits
- Circuit breaker patterns for fault tolerance
- Graceful degradation under high load

### Authentication
- JWT-based authentication
- API key management
- Multi-factor authentication support

## 📈 Scaling & Deployment

### Horizontal Scaling
- Dynamic agent pool scaling based on load
- Load balancing across agent instances
- Health-based failover mechanisms

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ backend/
EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Configuration
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ia-influencer-agents
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ia-influencer-agents
  template:
    metadata:
      labels:
        app: ia-influencer-agents
    spec:
      containers:
      - name: agents
        image: ia-influencer-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```
