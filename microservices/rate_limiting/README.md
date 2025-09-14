# ⚡ Rate Limiting Module - Enterprise Microservices

**© FAHED MLAIEL 2024-2025 - PROPRIÉTÉ INTELLECTUELLE STRICTE**  
**⚠️ ARCHITECTURE CONFIDENTIELLE - NIVEAU ENTERPRISE UNIQUEMENT**

## 🎯 Overview

Advanced rate limiting module for enterprise microservices architecture. Provides intelligent traffic control, DDoS protection, and API quota management with distributed rate limiting and real-time monitoring.

## 🏗️ Architecture

```
rate_limiting/
├── __init__.py                      # Module exports
├── index.py                         # Entry point
├── README.md                        # This documentation
├── token_bucket_limiter.py         # Token bucket algorithm
├── leaky_bucket_limiter.py         # Leaky bucket algorithm
├── sliding_window_limiter.py       # Sliding window algorithm
├── fixed_window_limiter.py         # Fixed window algorithm
├── redis_distributed_limiter.py    # Redis-based distributed limiting
├── memory_limiter.py               # In-memory rate limiting
├── adaptive_limiter.py             # AI-powered adaptive limiting
├── quota_manager.py                # API quota management
├── ddos_protection.py              # DDoS protection
├── rate_limit_controller.py        # Central controller
└── monitoring.py                   # Rate limiting monitoring
```

## ✨ Features

### 🚀 Multiple Algorithms
- **Token Bucket** - Burst traffic handling
- **Leaky Bucket** - Smooth traffic shaping
- **Sliding Window** - Precise rate control
- **Fixed Window** - Simple time-based limiting
- **Adaptive** - AI-powered dynamic limits

### 🌐 Distributed Support
- Redis-based coordination
- Consistent cross-instance limiting
- Multi-region synchronization
- Cluster-aware rate limiting

### 🛡️ Protection Features
- DDoS attack mitigation
- API abuse prevention
- Quota enforcement
- Burst protection

### 📊 Intelligent Monitoring
- Real-time rate limit metrics
- Violation detection
- Performance analytics
- Predictive scaling

## 🚀 Quick Start

### Basic Usage

```python
from microservices.rate_limiting import RateLimitController
from microservices.rate_limiting.algorithms import TokenBucketLimiter

# Create rate limit controller
controller = RateLimitController()

# Configure rate limits
await controller.configure_rate_limit(
    service="api-service",
    algorithm="token_bucket",
    rate=1000,  # requests per minute
    burst=100   # burst capacity
)

# Check rate limit
allowed = await controller.is_allowed(
    service="api-service",
    identifier="user_123",
    cost=1
)

if allowed:
    # Process request
    print("Request allowed")
else:
    # Rate limited
    print("Rate limit exceeded")
```

### Advanced Configuration

```python
from microservices.rate_limiting import (
    RateLimitConfig,
    AdaptiveLimiter,
    RedisDistributedLimiter
)

# Configure distributed rate limiting
config = RateLimitConfig(
    redis_url="redis://localhost:6379",
    enable_distributed=True,
    enable_adaptive=True,
    monitoring_enabled=True
)

# Create adaptive limiter
adaptive_limiter = AdaptiveLimiter(config)

# AI-powered rate limiting
result = await adaptive_limiter.check_limit(
    identifier="api_user_456",
    context={
        "user_tier": "premium",
        "endpoint": "/api/v1/data",
        "time_of_day": 14,
        "historical_usage": 0.7
    }
)
```

## 🎯 Rate Limiting Algorithms

### Token Bucket
```python
from microservices.rate_limiting import TokenBucketLimiter

# Create token bucket limiter
limiter = TokenBucketLimiter(
    capacity=100,      # bucket capacity
    refill_rate=10,    # tokens per second
    refill_period=1    # refill interval
)

# Check if request is allowed
allowed = await limiter.consume(
    identifier="user_123",
    tokens=1
)
```

### Sliding Window
```python
from microservices.rate_limiting import SlidingWindowLimiter

# Create sliding window limiter
limiter = SlidingWindowLimiter(
    window_size=60,    # 60 seconds
    max_requests=100   # 100 requests per window
)

# Check rate limit
allowed = await limiter.is_allowed(
    identifier="user_123",
    timestamp=time.time()
)
```

### Leaky Bucket
```python
from microservices.rate_limiting import LeakyBucketLimiter

# Create leaky bucket limiter
limiter = LeakyBucketLimiter(
    capacity=50,       # bucket capacity
    leak_rate=5        # requests per second
)

# Add request to bucket
allowed = await limiter.add_request(
    identifier="user_123"
)
```

### Adaptive AI Limiter
```python
from microservices.rate_limiting import AdaptiveLimiter

# Create AI-powered adaptive limiter
limiter = AdaptiveLimiter()

# Train the model
training_data = {
    'user_behavior': historical_usage_patterns,
    'system_metrics': performance_data,
    'attack_patterns': security_events
}

await limiter.train_model(training_data)

# Dynamic rate limiting
allowed = await limiter.intelligent_limit_check(
    identifier="user_123",
    request_context={
        "endpoint": "/api/heavy-computation",
        "user_reputation": 0.95,
        "system_load": 0.6,
        "threat_level": "low"
    }
)
```

## 🌐 Distributed Rate Limiting

### Redis-Based Coordination
```python
from microservices.rate_limiting import RedisDistributedLimiter

# Create distributed limiter
limiter = RedisDistributedLimiter(
    redis_url="redis://redis-cluster:6379",
    key_prefix="rate_limit:",
    synchronization_interval=100  # sync every 100ms
)

# Distributed rate limiting
result = await limiter.check_distributed_limit(
    service="api-service",
    identifier="global_user_123",
    limit=1000,
    window=60
)

print(f"Allowed: {result.allowed}")
print(f"Remaining: {result.remaining}")
print(f"Reset time: {result.reset_time}")
```

### Multi-Region Synchronization
```python
# Configure multi-region rate limiting
regions = ["us-east-1", "us-west-2", "eu-west-1"]

for region in regions:
    regional_limiter = RedisDistributedLimiter(
        redis_url=f"redis://{region}-redis:6379",
        region=region,
        global_sync_enabled=True
    )
    
    await controller.register_regional_limiter(region, regional_limiter)

# Global rate limiting across regions
allowed = await controller.check_global_limit(
    identifier="global_user_456",
    service="api-service"
)
```

## 🛡️ DDoS Protection

### Attack Detection
```python
from microservices.rate_limiting import DDoSProtection

# Configure DDoS protection
ddos_protection = DDoSProtection(
    baseline_rps=1000,           # normal requests per second
    attack_threshold_multiplier=5, # 5x normal = attack
    detection_window=30,         # 30 second detection window
    mitigation_duration=300      # 5 minute mitigation
)

# Real-time attack detection
threat_level = await ddos_protection.analyze_traffic(
    source_ip="192.168.1.100",
    request_rate=5000,
    request_pattern={
        "user_agent_diversity": 0.1,
        "endpoint_diversity": 0.2,
        "geographic_spread": 0.1
    }
)

if threat_level > 0.8:
    # Apply aggressive rate limiting
    await controller.apply_emergency_limits("api-service")
```

### Intelligent Mitigation
```python
# AI-powered attack mitigation
mitigation_strategy = await ddos_protection.generate_mitigation_strategy(
    attack_vector="volumetric",
    attack_intensity=0.9,
    legitimate_traffic_percentage=0.1
)

# Apply mitigation
await controller.apply_mitigation_strategy(mitigation_strategy)
```

## 📊 API Quota Management

### User Tier Management
```python
from microservices.rate_limiting import QuotaManager

# Create quota manager
quota_manager = QuotaManager()

# Define user tiers
tiers = {
    "free": {"daily_quota": 1000, "rate_limit": 10},
    "premium": {"daily_quota": 10000, "rate_limit": 100},
    "enterprise": {"daily_quota": 100000, "rate_limit": 1000}
}

await quota_manager.configure_tiers(tiers)

# Check quota
quota_status = await quota_manager.check_quota(
    user_id="user_123",
    tier="premium",
    operation="api_call"
)

print(f"Quota remaining: {quota_status.remaining}")
print(f"Quota resets: {quota_status.reset_time}")
```

### Overage Handling
```python
# Configure overage policies
overage_policy = {
    "free": {"action": "block", "grace_period": 0},
    "premium": {"action": "throttle", "grace_percentage": 10},
    "enterprise": {"action": "bill", "overage_rate": 0.001}
}

await quota_manager.configure_overage_policies(overage_policy)

# Handle quota exceeded
result = await quota_manager.handle_quota_exceeded(
    user_id="user_123",
    tier="premium",
    overage_amount=50
)
```

## 🔧 Configuration

### Environment Variables
```bash
# Rate Limiting Configuration
RATE_LIMIT_ALGORITHM=token_bucket
RATE_LIMIT_REDIS_URL=redis://localhost:6379
RATE_LIMIT_DEFAULT_RATE=1000
RATE_LIMIT_DEFAULT_BURST=100

# DDoS Protection
DDOS_PROTECTION_ENABLED=true
DDOS_BASELINE_RPS=1000
DDOS_THRESHOLD_MULTIPLIER=5
DDOS_DETECTION_WINDOW=30

# Distributed Settings
RATE_LIMIT_DISTRIBUTED=true
RATE_LIMIT_REGION=us-east-1
RATE_LIMIT_CLUSTER_SYNC=true
```

### YAML Configuration
```yaml
rate_limiting:
  default_algorithm: adaptive
  
  algorithms:
    token_bucket:
      default_capacity: 100
      default_refill_rate: 10
      refill_period: 1
    
    sliding_window:
      window_size: 60
      precision: 1000
    
    adaptive:
      model_type: neural_network
      training_interval: 3600
      adaptation_rate: 0.1
  
  distributed:
    enabled: true
    backend: redis
    redis:
      url: redis://localhost:6379
      pool_size: 10
      timeout: 1
    
    synchronization:
      interval_ms: 100
      batch_size: 1000
  
  ddos_protection:
    enabled: true
    baseline_rps: 1000
    attack_threshold: 5.0
    detection_window: 30
    mitigation_duration: 300
    
    mitigation_strategies:
      - type: rate_limit_reduction
        factor: 0.1
      - type: captcha_challenge
        threshold: 0.7
      - type: ip_blocking
        duration: 3600
```

## 📈 Monitoring & Observability

### Prometheus Metrics
```python
# Exported metrics
rate_limit_requests_total{service="api-service", status="allowed"}
rate_limit_requests_total{service="api-service", status="denied"}
rate_limit_bucket_capacity{service="api-service", algorithm="token_bucket"}
rate_limit_bucket_tokens{service="api-service", algorithm="token_bucket"}
rate_limit_response_time_seconds{service="api-service"}
rate_limit_quota_usage{user_tier="premium", quota_type="daily"}
ddos_attacks_detected_total{severity="high"}
ddos_mitigation_duration_seconds{strategy="rate_limit_reduction"}
```

### Real-time Dashboard
```python
# Get rate limiting dashboard data
dashboard_data = await controller.get_dashboard_data()

print(f"Total requests: {dashboard_data['total_requests']}")
print(f"Blocked requests: {dashboard_data['blocked_requests']}")
print(f"Top violators: {dashboard_data['top_violators']}")
print(f"Active attacks: {dashboard_data['active_attacks']}")
```

### Alerting
```python
# Configure alerting
alert_rules = [
    {
        "name": "high_rate_limit_violations",
        "condition": "rate_limit_denied_rate > 0.1",
        "severity": "warning",
        "duration": "5m"
    },
    {
        "name": "ddos_attack_detected",
        "condition": "ddos_attacks_detected > 0",
        "severity": "critical",
        "duration": "1m"
    }
]

await controller.configure_alerts(alert_rules)
```

## 🧪 Testing

### Unit Tests
```bash
# Run rate limiting tests
python -m pytest microservices/rate_limiting/tests/

# Test specific algorithm
python -m pytest microservices/rate_limiting/tests/test_token_bucket.py -v
```

### Load Testing
```bash
# Performance testing
python -m pytest microservices/rate_limiting/tests/performance/ --benchmark-only

# DDoS simulation
python -m pytest microservices/rate_limiting/tests/ddos_simulation.py
```

### Integration Tests
```bash
# Test with Redis
python -m pytest microservices/rate_limiting/tests/integration/test_redis.py

# Test distributed limiting
python -m pytest microservices/rate_limiting/tests/integration/test_distributed.py
```

## 🚀 Deployment

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rate-limit-controller
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rate-limit-controller
  template:
    metadata:
      labels:
        app: rate-limit-controller
    spec:
      containers:
      - name: controller
        image: ainflue/rate-limiter:latest
        ports:
        - containerPort: 8080
        env:
        - name: RATE_LIMIT_REDIS_URL
          value: "redis://redis-service:6379"
        - name: DDOS_PROTECTION_ENABLED
          value: "true"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

### Redis Configuration
```yaml
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command: ["redis-server", "--appendonly", "yes"]
```

## 📞 Support

### Team Contact
- **Lead Developer:** Fahed Mlaiel (mlaiel@live.de)
- **Team:** Rate Limiting Team
- **Expertise:** Distributed rate limiting, DDoS protection, API security

### Documentation
- [Algorithm Comparison](./docs/algorithms.md)
- [DDoS Protection Guide](./docs/ddos-protection.md)
- [Performance Tuning](./docs/performance.md)
- [Troubleshooting](./docs/troubleshooting.md)

---

**Enterprise Rate Limiting Module - Production Ready**  
*Part of Ainflue Microservices Architecture*