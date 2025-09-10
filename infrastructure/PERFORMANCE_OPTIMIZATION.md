# ⚡ Ainflue Infrastructure Performance Optimization Guide

**Author:** Fahed Mlaiel <mlaiel@live.de>  
**Team:** Performance Engineer + SRE Specialist + Infrastructure Architect  
**Version:** 1.0.0  
**Last Updated:** January 2025  

## 📋 Table of Contents

1. [Performance Framework Overview](#performance-framework-overview)
2. [Application Performance Optimization](#application-performance-optimization)
3. [Database Performance Tuning](#database-performance-tuning)
4. [Infrastructure Optimization](#infrastructure-optimization)
5. [Content Delivery Optimization](#content-delivery-optimization)
6. [AI Processing Performance](#ai-processing-performance)
7. [Creator Economy Optimizations](#creator-economy-optimizations)
8. [Monitoring and Benchmarking](#monitoring-and-benchmarking)

---

## 🎯 Performance Framework Overview

### Performance Targets for Creator Economy

The Ainflue platform maintains **industry-leading performance standards** specifically optimized for creator workflows, ensuring seamless content creation, processing, and monetization experiences.

### Core Performance Metrics

```yaml
Performance_SLAs:
  API_Response_Time:
    Target: <100ms (95th percentile)
    Critical_Threshold: <500ms (99th percentile)
    Measurement: End-to-end API response time
    
  Content_Upload_Speed:
    Target: >10MB/s for files >100MB
    Critical_Threshold: >5MB/s minimum
    Measurement: Upload throughput to S3
    
  AI_Processing_Time:
    Target: <30s for standard content analysis
    Critical_Threshold: <120s for complex processing
    Measurement: Queue to completion time
    
  Database_Query_Performance:
    Target: <50ms (95th percentile)
    Critical_Threshold: <200ms (99th percentile)
    Measurement: Query execution time
    
  Page_Load_Time:
    Target: <2s First Contentful Paint
    Critical_Threshold: <5s Largest Contentful Paint
    Measurement: Web Vitals metrics
    
  Creator_Revenue_Processing:
    Target: <5s for payment completion
    Critical_Threshold: <30s for complex transactions
    Measurement: Payment processing pipeline
```

### Performance Architecture Principles

```yaml
Optimization_Principles:
  Caching_Strategy: Multi-layer caching (CDN, Application, Database)
  Horizontal_Scaling: Auto-scaling based on demand patterns
  Asynchronous_Processing: Non-blocking operations for heavy tasks
  Data_Locality: Content served from nearest edge locations
  Resource_Pooling: Efficient resource utilization and sharing
  Predictive_Scaling: AI-powered capacity planning
  Performance_Budgets: Defined performance constraints
  Continuous_Optimization: Real-time performance monitoring
```

---

## 🚀 Application Performance Optimization

### Code-Level Optimizations

#### Go Application Performance Tuning
```go
// performance_config.go
package config

import (
    "runtime"
    "runtime/debug"
    "time"
)

// OptimizeRuntime configures Go runtime for optimal performance
func OptimizeRuntime() {
    // Set GOMAXPROCS to match container CPU limits
    numCPU := runtime.NumCPU()
    runtime.GOMAXPROCS(numCPU)
    
    // Optimize garbage collection
    debug.SetGCPercent(100) // Default 100%, adjust based on memory patterns
    debug.SetMemoryLimit(1 << 30) // 1GB memory limit
    
    // Set max threads for I/O operations
    debug.SetMaxThreads(10000)
}

// Connection pool optimization
type DatabaseConfig struct {
    MaxOpenConns    int           `json:"max_open_conns"`
    MaxIdleConns    int           `json:"max_idle_conns"`
    ConnMaxLifetime time.Duration `json:"conn_max_lifetime"`
    ConnMaxIdleTime time.Duration `json:"conn_max_idle_time"`
}

var OptimalDBConfig = DatabaseConfig{
    MaxOpenConns:    100, // Adjust based on concurrent load
    MaxIdleConns:    10,  // Keep some connections warm
    ConnMaxLifetime: 5 * time.Minute,
    ConnMaxIdleTime: 30 * time.Second,
}

// HTTP client optimization
type HTTPClientConfig struct {
    MaxIdleConns        int
    MaxIdleConnsPerHost int
    IdleConnTimeout     time.Duration
    Timeout             time.Duration
}

var OptimalHTTPConfig = HTTPClientConfig{
    MaxIdleConns:        100,
    MaxIdleConnsPerHost: 10,
    IdleConnTimeout:     90 * time.Second,
    Timeout:             30 * time.Second,
}
```

#### Caching Strategy Implementation
```go
// cache_optimization.go
package cache

import (
    "context"
    "encoding/json"
    "time"
    "github.com/go-redis/redis/v8"
)

type MultiLevelCache struct {
    L1Cache map[string]interface{} // In-memory cache
    L2Cache *redis.Client          // Redis cache
    L3Cache *S3Cache              // S3 for large objects
}

// Intelligent caching based on content type and access patterns
func (c *MultiLevelCache) Get(ctx context.Context, key string) (interface{}, error) {
    // L1: Check in-memory cache first (fastest)
    if value, exists := c.L1Cache[key]; exists {
        return value, nil
    }
    
    // L2: Check Redis cache (fast)
    if value, err := c.L2Cache.Get(ctx, key).Result(); err == nil {
        var result interface{}
        json.Unmarshal([]byte(value), &result)
        
        // Populate L1 cache for future requests
        c.L1Cache[key] = result
        return result, nil
    }
    
    // L3: Check S3 cache for large objects (slower but cost-effective)
    if value, err := c.L3Cache.Get(ctx, key); err == nil {
        // Populate both L1 and L2 caches
        c.L1Cache[key] = value
        jsonValue, _ := json.Marshal(value)
        c.L2Cache.Set(ctx, key, jsonValue, time.Hour)
        return value, nil
    }
    
    return nil, ErrCacheNotFound
}

// Smart cache eviction based on access patterns
func (c *MultiLevelCache) Set(ctx context.Context, key string, value interface{}, ttl time.Duration) error {
    // Always store in L1 for immediate access
    c.L1Cache[key] = value
    
    // Store in L2 (Redis) for persistence and sharing across instances
    jsonValue, _ := json.Marshal(value)
    c.L2Cache.Set(ctx, key, jsonValue, ttl)
    
    // Store large objects (>1MB) in L3 (S3) for cost efficiency
    if size := estimateSize(value); size > 1024*1024 {
        return c.L3Cache.Set(ctx, key, value, ttl)
    }
    
    return nil
}
```

#### API Request Optimization
```go
// api_optimization.go
package api

import (
    "net/http"
    "sync"
    "time"
)

// Request deduplication to prevent duplicate processing
type RequestDeduplicator struct {
    inFlight map[string]*sync.WaitGroup
    mutex    sync.RWMutex
}

func (rd *RequestDeduplicator) Execute(key string, fn func() (interface{}, error)) (interface{}, error) {
    rd.mutex.Lock()
    
    // Check if request is already in flight
    if wg, exists := rd.inFlight[key]; exists {
        rd.mutex.Unlock()
        wg.Wait() // Wait for existing request to complete
        return rd.getFromCache(key)
    }
    
    // Mark request as in flight
    wg := &sync.WaitGroup{}
    wg.Add(1)
    rd.inFlight[key] = wg
    rd.mutex.Unlock()
    
    // Execute the function
    result, err := fn()
    
    // Clean up and notify waiters
    rd.mutex.Lock()
    delete(rd.inFlight, key)
    rd.mutex.Unlock()
    wg.Done()
    
    return result, err
}

// Response compression middleware
func CompressionMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Enable compression for responses >1KB
        if supportsCompression(r) {
            w.Header().Set("Content-Encoding", "gzip")
            w.Header().Set("Vary", "Accept-Encoding")
            
            gzipWriter := gzip.NewWriter(w)
            defer gzipWriter.Close()
            
            wrappedWriter := &gzipResponseWriter{
                Writer:         gzipWriter,
                ResponseWriter: w,
            }
            
            next.ServeHTTP(wrappedWriter, r)
        } else {
            next.ServeHTTP(w, r)
        }
    })
}
```

### Kubernetes Resource Optimization

#### Pod Resource Configuration
```yaml
# optimized-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ainflue-api-optimized
  namespace: ainflue
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 50%
      maxUnavailable: 25%
  selector:
    matchLabels:
      app: ainflue-api
  template:
    metadata:
      labels:
        app: ainflue-api
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      # Performance optimizations
      nodeSelector:
        node-type: "performance"
      
      # Resource allocation based on profiling
      containers:
      - name: api
        image: ainflue/api:optimized
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 8080
          name: metrics
        
        # Optimized resource allocation
        resources:
          requests:
            cpu: 500m      # Guaranteed CPU
            memory: 512Mi  # Guaranteed memory
          limits:
            cpu: 2000m     # Burst capacity
            memory: 2Gi    # Maximum memory
        
        # Performance-tuned environment variables
        env:
        - name: GOMAXPROCS
          valueFrom:
            resourceFieldRef:
              resource: limits.cpu
              divisor: 1
        - name: GOMEMLIMIT
          valueFrom:
            resourceFieldRef:
              resource: limits.memory
              divisor: 1
        - name: GOGC
          value: "100"
        - name: DB_POOL_SIZE
          value: "50"
        - name: CACHE_SIZE
          value: "100MB"
        
        # Optimized health checks
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        
        # Security and performance
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
      
      # Performance-oriented pod settings
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      terminationGracePeriodSeconds: 30
      
      # Affinity rules for optimal distribution
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - ainflue-api
              topologyKey: kubernetes.io/hostname
```

#### Advanced Auto-Scaling Configuration
```yaml
# advanced-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ainflue-api-hpa-advanced
  namespace: ainflue
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ainflue-api
  minReplicas: 3
  maxReplicas: 50
  
  # Multiple metrics for intelligent scaling
  metrics:
  # CPU-based scaling
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  
  # Memory-based scaling
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  
  # Custom metrics: API request rate
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  
  # Custom metrics: Response time
  - type: Pods
    pods:
      metric:
        name: response_time_p95
      target:
        type: AverageValue
        averageValue: "100m"  # 100ms
  
  # Scaling behavior for predictable performance
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 5 minutes
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Min
    
    scaleUp:
      stabilizationWindowSeconds: 60   # 1 minute
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
      - type: Pods
        value: 4
        periodSeconds: 60
      selectPolicy: Max
```

---

## 🗄️ Database Performance Tuning

### PostgreSQL Optimization

#### Advanced Configuration Parameters
```sql
-- postgresql-performance.conf
-- Memory configuration optimized for 16GB instance
shared_buffers = 4GB                    -- 25% of total memory
effective_cache_size = 12GB             -- 75% of total memory
work_mem = 64MB                         -- Per connection work memory
maintenance_work_mem = 512MB            -- For maintenance operations
wal_buffers = 16MB                      -- WAL buffer size

-- CPU and I/O optimization
max_worker_processes = 8                -- Number of background workers
max_parallel_workers_per_gather = 4     -- Parallel query workers
max_parallel_workers = 8                -- Total parallel workers
max_parallel_maintenance_workers = 4    -- Parallel maintenance workers

-- Checkpoint and WAL optimization
checkpoint_completion_target = 0.9      -- Spread checkpoint writes
wal_level = replica                     -- For replication
max_wal_size = 2GB                      -- Maximum WAL size
min_wal_size = 1GB                      -- Minimum WAL size
checkpoint_timeout = 10min              -- Checkpoint frequency

-- Connection optimization
max_connections = 200                   -- Maximum connections
shared_preload_libraries = 'pg_stat_statements,auto_explain'

-- Query optimization
random_page_cost = 1.1                  -- SSD optimization
effective_io_concurrency = 200          -- Concurrent I/O operations
default_statistics_target = 100         -- Statistics detail level

-- Logging and monitoring
log_min_duration_statement = 1000       -- Log slow queries (1s+)
log_checkpoints = on                    -- Log checkpoint info
log_connections = on                    -- Log connections
log_disconnections = on                 -- Log disconnections
log_lock_waits = on                     -- Log lock waits
```

#### Index Optimization Strategy
```sql
-- index-optimization.sql

-- Creator-centric indices for fast lookups
CREATE INDEX CONCURRENTLY idx_creators_username_hash 
ON creators USING hash(username);

CREATE INDEX CONCURRENTLY idx_creators_email_hash 
ON creators USING hash(email);

-- Content upload optimization
CREATE INDEX CONCURRENTLY idx_uploads_creator_status_created 
ON uploads(creator_id, status, created_at DESC) 
WHERE status IN ('processing', 'completed');

-- Revenue processing optimization
CREATE INDEX CONCURRENTLY idx_transactions_creator_status_date
ON transactions(creator_id, status, created_at)
WHERE status = 'pending';

-- Subscription queries optimization
CREATE INDEX CONCURRENTLY idx_subscriptions_creator_active_tier
ON subscriptions(creator_id, tier)
WHERE is_active = true;

-- Content discovery optimization
CREATE INDEX CONCURRENTLY idx_content_category_trending
ON content(category, trending_score DESC, created_at DESC)
WHERE is_published = true;

-- Full-text search optimization
CREATE INDEX CONCURRENTLY idx_content_search
ON content USING gin(to_tsvector('english', title || ' ' || description))
WHERE is_published = true;

-- Partial indices for common queries
CREATE INDEX CONCURRENTLY idx_uploads_recent_processing
ON uploads(created_at DESC)
WHERE status = 'processing' AND created_at > NOW() - INTERVAL '24 hours';

-- Covering indices to avoid table lookups
CREATE INDEX CONCURRENTLY idx_creators_dashboard_data
ON creators(id) INCLUDE (username, display_name, follower_count, total_revenue);
```

#### Query Performance Optimization
```sql
-- query-optimization.sql

-- Optimized creator dashboard query
EXPLAIN (ANALYZE, BUFFERS) 
WITH creator_stats AS (
    SELECT 
        c.id,
        c.username,
        c.display_name,
        COUNT(u.id) as upload_count,
        SUM(CASE WHEN u.created_at > NOW() - INTERVAL '30 days' THEN 1 ELSE 0 END) as recent_uploads,
        COALESCE(SUM(t.amount), 0) as total_revenue
    FROM creators c
    LEFT JOIN uploads u ON c.id = u.creator_id AND u.status = 'completed'
    LEFT JOIN transactions t ON c.id = t.creator_id AND t.status = 'completed'
    WHERE c.id = $1
    GROUP BY c.id, c.username, c.display_name
)
SELECT * FROM creator_stats;

-- Optimized content feed query with pagination
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    c.id,
    c.title,
    c.thumbnail_url,
    cr.username as creator_name,
    c.view_count,
    c.like_count,
    c.created_at
FROM content c
JOIN creators cr ON c.creator_id = cr.id
WHERE c.is_published = true
    AND c.category = $1
    AND c.created_at < $2  -- Cursor-based pagination
ORDER BY c.trending_score DESC, c.created_at DESC
LIMIT 20;

-- Batch processing for revenue calculations
DO $$
DECLARE
    batch_size INTEGER := 1000;
    offset_val INTEGER := 0;
    processed_count INTEGER;
BEGIN
    LOOP
        WITH batch AS (
            SELECT id, creator_id, amount
            FROM transactions
            WHERE status = 'pending'
                AND created_at < NOW() - INTERVAL '1 hour'
            ORDER BY id
            LIMIT batch_size OFFSET offset_val
        )
        UPDATE transactions 
        SET status = 'processing', updated_at = NOW()
        WHERE id IN (SELECT id FROM batch);
        
        GET DIAGNOSTICS processed_count = ROW_COUNT;
        
        EXIT WHEN processed_count = 0;
        
        offset_val := offset_val + batch_size;
        
        -- Commit in batches to avoid long-running transactions
        COMMIT;
    END LOOP;
END $$;
```

### Redis Performance Optimization

#### Redis Configuration Tuning
```conf
# redis-performance.conf

# Memory optimization
maxmemory 4gb
maxmemory-policy allkeys-lru
maxmemory-samples 10

# Persistence optimization for performance
save 900 1     # Save if at least 1 key changed in 900 seconds
save 300 10    # Save if at least 10 keys changed in 300 seconds
save 60 10000  # Save if at least 10000 keys changed in 60 seconds

# Disable RDB snapshots for pure cache use case
# save ""

# AOF configuration for durability vs performance balance
appendonly yes
appendfsync everysec  # Good balance of performance and durability
no-appendfsync-on-rewrite yes
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Network optimization
tcp-keepalive 300
tcp-backlog 511
timeout 0

# Client optimization
maxclients 10000

# Slow log configuration
slowlog-log-slower-than 10000  # 10ms
slowlog-max-len 128

# Memory usage optimization
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64

# Background saving optimization
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
```

#### Redis Data Structure Optimization
```python
# redis_optimization.py
import redis
import json
import pickle
from typing import Any, Optional

class OptimizedRedisClient:
    def __init__(self, host: str, port: int, db: int = 0):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=False,  # Keep binary for performance
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            max_connections=100,
            connection_pool_kwargs={
                'max_connections': 100,
                'retry_on_timeout': True
            }
        )
    
    def set_creator_cache(self, creator_id: str, data: dict, ttl: int = 3600):
        """Optimized creator data caching with compression"""
        key = f"creator:{creator_id}"
        
        # Use pickle for better performance with complex objects
        serialized_data = pickle.dumps(data)
        
        # Use pipeline for atomic operations
        pipe = self.client.pipeline()
        pipe.set(key, serialized_data, ex=ttl)
        pipe.execute()
    
    def get_creator_cache(self, creator_id: str) -> Optional[dict]:
        """Fast creator data retrieval"""
        key = f"creator:{creator_id}"
        data = self.client.get(key)
        
        if data:
            return pickle.loads(data)
        return None
    
    def cache_trending_content(self, content_list: list, ttl: int = 300):
        """Cache trending content with sorted sets for fast retrieval"""
        pipe = self.client.pipeline()
        
        # Use sorted set for trending content
        trending_key = "trending:content"
        pipe.delete(trending_key)
        
        for i, content in enumerate(content_list):
            score = len(content_list) - i  # Higher score for better ranking
            pipe.zadd(trending_key, {content['id']: score})
            
            # Cache individual content data
            content_key = f"content:{content['id']}"
            pipe.set(content_key, pickle.dumps(content), ex=ttl)
        
        pipe.expire(trending_key, ttl)
        pipe.execute()
    
    def get_trending_content(self, limit: int = 20) -> list:
        """Fast trending content retrieval"""
        trending_key = "trending:content"
        content_ids = self.client.zrevrange(trending_key, 0, limit - 1)
        
        if not content_ids:
            return []
        
        # Batch get content data
        pipe = self.client.pipeline()
        for content_id in content_ids:
            pipe.get(f"content:{content_id.decode()}")
        
        results = pipe.execute()
        
        content_list = []
        for result in results:
            if result:
                content_list.append(pickle.loads(result))
        
        return content_list
    
    def increment_view_count(self, content_id: str) -> int:
        """High-performance view counting with batching"""
        key = f"views:{content_id}"
        
        # Use Redis increment for atomic operations
        new_count = self.client.incr(key)
        
        # Set expiration on first increment
        if new_count == 1:
            self.client.expire(key, 86400)  # 24 hours
        
        return new_count
```

---

## 🏗️ Infrastructure Optimization

### Container and Kubernetes Optimization

#### Node Configuration Optimization
```yaml
# optimized-nodegroup.yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: ainflue-prod-optimized
  region: us-east-1

nodeGroups:
  # Performance-optimized general purpose nodes
  - name: performance-general
    instanceType: c5.2xlarge  # CPU-optimized
    minSize: 3
    maxSize: 20
    desiredCapacity: 5
    
    # EBS optimization for I/O performance
    volumeSize: 100
    volumeType: gp3
    volumeIOPS: 3000
    volumeThroughput: 125
    
    # Network optimization
    privateNetworking: true
    
    # Performance tuning
    kubeletExtraConfig:
      maxPods: 110
      evictionHard:
        memory.available: "200Mi"
        nodefs.available: "10%"
      evictionSoft:
        memory.available: "500Mi"
        nodefs.available: "15%"
      evictionSoftGracePeriod:
        memory.available: "1m30s"
        nodefs.available: "2m"
      imageGCHighThresholdPercent: 85
      imageGCLowThresholdPercent: 80
      
    # Node labels for optimal scheduling
    labels:
      node-type: "performance"
      workload: "cpu-intensive"
    
    # Taints for dedicated workloads
    taints:
      performance: "true:NoSchedule"

  # Memory-optimized nodes for caching and data processing
  - name: memory-optimized
    instanceType: r5.xlarge
    minSize: 2
    maxSize: 10
    desiredCapacity: 3
    
    labels:
      node-type: "memory-optimized"
      workload: "memory-intensive"
    
    taints:
      memory-intensive: "true:NoSchedule"

  # GPU nodes for AI processing
  - name: gpu-nodes
    instanceType: p3.2xlarge
    minSize: 0
    maxSize: 5
    desiredCapacity: 1
    
    labels:
      node-type: "gpu"
      nvidia.com/gpu: "present"
    
    taints:
      nvidia.com/gpu: "true:NoSchedule"
```

#### Network Performance Optimization
```yaml
# network-optimization.yaml
apiVersion: v1
kind: Service
metadata:
  name: ainflue-api-optimized
  namespace: ainflue
  annotations:
    # AWS Load Balancer optimization
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: "tcp"
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
    
    # Connection optimization
    service.beta.kubernetes.io/aws-load-balancer-connection-idle-timeout: "60"
    service.beta.kubernetes.io/aws-load-balancer-connection-draining-timeout: "300"
    
    # Health check optimization
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-healthy-threshold: "2"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-unhealthy-threshold: "2"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-interval: "10"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-timeout: "6"
spec:
  type: LoadBalancer
  sessionAffinity: None  # Disable for better load distribution
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: ainflue-api

---
# Ingress optimization
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ainflue-ingress-optimized
  namespace: ainflue
  annotations:
    kubernetes.io/ingress.class: "nginx"
    
    # Performance optimizations
    nginx.ingress.kubernetes.io/proxy-buffering: "on"
    nginx.ingress.kubernetes.io/proxy-buffer-size: "128k"
    nginx.ingress.kubernetes.io/proxy-buffers-number: "4"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "60"
    
    # Connection optimization
    nginx.ingress.kubernetes.io/upstream-keepalive-connections: "320"
    nginx.ingress.kubernetes.io/upstream-keepalive-requests: "10000"
    nginx.ingress.kubernetes.io/upstream-keepalive-timeout: "60"
    
    # Compression
    nginx.ingress.kubernetes.io/enable-compression: "true"
    nginx.ingress.kubernetes.io/compression-level: "6"
    nginx.ingress.kubernetes.io/compression-min-length: "1000"
    
    # Rate limiting for DDoS protection
    nginx.ingress.kubernetes.io/rate-limit: "1000"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    
    # SSL optimization
    nginx.ingress.kubernetes.io/ssl-protocols: "TLSv1.2 TLSv1.3"
    nginx.ingress.kubernetes.io/ssl-ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256,ECDHE-RSA-AES128-GCM-SHA256"
    nginx.ingress.kubernetes.io/ssl-prefer-server-ciphers: "true"
spec:
  tls:
  - hosts:
    - api.ainflue.com
    secretName: ainflue-tls-optimized
  rules:
  - host: api.ainflue.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ainflue-api-optimized
            port:
              number: 80
```

---

## 🌐 Content Delivery Optimization

### CDN Configuration

#### CloudFront Performance Configuration
```json
{
  "DistributionConfig": {
    "CallerReference": "ainflue-optimized-cdn",
    "Comment": "Ainflue Optimized CDN for Creator Content",
    "DefaultRootObject": "index.html",
    "Origins": [
      {
        "Id": "ainflue-api-origin",
        "DomainName": "api.ainflue.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "https-only",
          "OriginSSLProtocols": {
            "Quantity": 2,
            "Items": ["TLSv1.2", "TLSv1.3"]
          },
          "OriginReadTimeout": 30,
          "OriginKeepaliveTimeout": 5
        }
      },
      {
        "Id": "s3-content-origin",
        "DomainName": "ainflue-content-prod.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": "origin-access-identity/cloudfront/ABCDEFG1234567"
        }
      }
    ],
    "DefaultCacheBehavior": {
      "TargetOriginId": "ainflue-api-origin",
      "ViewerProtocolPolicy": "redirect-to-https",
      "AllowedMethods": {
        "Quantity": 7,
        "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
        "CachedMethods": {
          "Quantity": 2,
          "Items": ["GET", "HEAD"]
        }
      },
      "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",  # Managed-CachingOptimized
      "OriginRequestPolicyId": "88a5eaf4-2fd4-4709-b370-b4c650ea3fcf",  # Managed-CORS-S3Origin
      "ResponseHeadersPolicyId": "67f7725c-6f97-4210-82d7-5512b31e9d03",  # Managed-SecurityHeadersPolicy
      "Compress": true,
      "FieldLevelEncryptionId": "",
      "RealtimeLogConfigArn": ""
    },
    "CacheBehaviors": [
      {
        "PathPattern": "/api/*",
        "TargetOriginId": "ainflue-api-origin",
        "ViewerProtocolPolicy": "https-only",
        "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
        "TTL": {
          "DefaultTTL": 300,    # 5 minutes for API responses
          "MaxTTL": 3600        # 1 hour maximum
        }
      },
      {
        "PathPattern": "/content/*",
        "TargetOriginId": "s3-content-origin",
        "ViewerProtocolPolicy": "https-only",
        "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",  # Managed-CachingOptimizedForUncompressedObjects
        "TTL": {
          "DefaultTTL": 86400,  # 24 hours for static content
          "MaxTTL": 31536000    # 1 year maximum
        }
      }
    ],
    "CustomErrorResponses": [
      {
        "ErrorCode": 404,
        "ResponsePagePath": "/404.html",
        "ResponseCode": "404",
        "ErrorCachingMinTTL": 300
      },
      {
        "ErrorCode": 500,
        "ResponsePagePath": "/500.html", 
        "ResponseCode": "500",
        "ErrorCachingMinTTL": 10
      }
    ],
    "PriceClass": "PriceClass_All",  # Global edge locations
    "Enabled": true,
    "HttpVersion": "http2",
    "IsIPV6Enabled": true,
    "WebACLId": "arn:aws:wafv2:us-east-1:account:global/webacl/ainflue-protection/id"
  }
}
```

#### S3 Performance Optimization
```yaml
# s3-optimization.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: s3-performance-config
  namespace: ainflue
data:
  # Transfer optimization
  MULTIPART_THRESHOLD: "64MB"      # Start multipart upload for files >64MB
  MULTIPART_CHUNKSIZE: "16MB"      # 16MB chunks for optimal performance
  MAX_CONCURRENCY: "10"            # Concurrent uploads/downloads
  MAX_BANDWIDTH: "1GB/s"           # Bandwidth limit per operation
  
  # Connection optimization
  USE_ACCELERATE_ENDPOINT: "true"  # S3 Transfer Acceleration
  ADDRESSING_STYLE: "virtual"      # Virtual hosted-style requests
  SIGNATURE_VERSION: "s3v4"        # Signature version
  
  # Regional optimization
  PRIMARY_REGION: "us-east-1"
  REPLICA_REGIONS: "eu-west-1,ap-southeast-1"
  
  # Caching optimization
  CACHE_CONTROL_IMAGES: "public, max-age=31536000, immutable"  # 1 year
  CACHE_CONTROL_VIDEOS: "public, max-age=2592000"              # 30 days
  CACHE_CONTROL_AUDIO: "public, max-age=2592000"               # 30 days
  CACHE_CONTROL_DOCUMENTS: "public, max-age=86400"             # 1 day
```

#### Edge Computing with Lambda@Edge
```javascript
// edge-optimization.js
'use strict';

// CloudFront Lambda@Edge function for performance optimization
exports.handler = async (event, context) => {
    const request = event.Records[0].cf.request;
    const headers = request.headers;
    
    // Device detection for responsive content delivery
    const userAgent = headers['user-agent'][0].value.toLowerCase();
    const isMobile = /mobile|android|iphone|ipad/.test(userAgent);
    const isTablet = /tablet|ipad/.test(userAgent);
    
    // Add device headers for backend optimization
    headers['x-device-type'] = [{
        key: 'X-Device-Type',
        value: isMobile ? 'mobile' : isTablet ? 'tablet' : 'desktop'
    }];
    
    // Geographic optimization
    const country = headers['cloudfront-viewer-country'][0].value;
    const isEurope = ['DE', 'FR', 'UK', 'IT', 'ES', 'NL', 'BE', 'CH'].includes(country);
    const isAsia = ['JP', 'KR', 'CN', 'SG', 'IN', 'AU'].includes(country);
    
    // Route to optimal origin based on geography
    if (isEurope) {
        request.origin = {
            custom: {
                domainName: 'api-eu.ainflue.com',
                port: 443,
                protocol: 'https',
                path: ''
            }
        };
    } else if (isAsia) {
        request.origin = {
            custom: {
                domainName: 'api-asia.ainflue.com',
                port: 443,
                protocol: 'https',
                path: ''
            }
        };
    }
    
    // Content type optimization for creators
    const uri = request.uri;
    
    // Image optimization
    if (uri.match(/\.(jpg|jpeg|png|webp)$/i)) {
        const accept = headers.accept ? headers.accept[0].value : '';
        
        // Serve WebP to supported browsers
        if (accept.includes('image/webp')) {
            request.uri = uri.replace(/\.(jpg|jpeg|png)$/i, '.webp');
        }
        
        // Add image optimization parameters
        const quality = isMobile ? '75' : '90';
        request.querystring = request.querystring 
            ? `${request.querystring}&q=${quality}` 
            : `q=${quality}`;
    }
    
    // Video streaming optimization
    if (uri.match(/\.(mp4|mov|avi)$/i)) {
        // Add adaptive bitrate parameters for mobile
        if (isMobile) {
            request.querystring = request.querystring 
                ? `${request.querystring}&bitrate=low` 
                : 'bitrate=low';
        }
    }
    
    // Security headers for performance
    headers['x-frame-options'] = [{key: 'X-Frame-Options', value: 'DENY'}];
    headers['x-content-type-options'] = [{key: 'X-Content-Type-Options', value: 'nosniff'}];
    headers['strict-transport-security'] = [{
        key: 'Strict-Transport-Security', 
        value: 'max-age=31536000; includeSubDomains; preload'
    }];
    
    return request;
};

// Lambda@Edge response function for optimization
exports.responseHandler = async (event, context) => {
    const response = event.Records[0].cf.response;
    const headers = response.headers;
    
    // Performance headers
    headers['cache-control'] = [{
        key: 'Cache-Control',
        value: 'public, max-age=31536000, immutable'
    }];
    
    // Compression optimization
    headers['content-encoding'] = [{key: 'Content-Encoding', value: 'gzip'}];
    
    // Connection optimization
    headers['connection'] = [{key: 'Connection', value: 'keep-alive'}];
    
    return response;
};
```

---

## 🤖 AI Processing Performance

### GPU Optimization for Content Processing

#### CUDA Performance Configuration
```yaml
# gpu-optimized-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-processor-gpu
  namespace: ainflue
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-processor
  template:
    metadata:
      labels:
        app: ai-processor
    spec:
      nodeSelector:
        nvidia.com/gpu: "present"
      
      tolerations:
      - key: nvidia.com/gpu
        operator: Equal
        value: "true"
        effect: NoSchedule
      
      containers:
      - name: ai-processor
        image: ainflue/ai-processor:gpu-optimized
        
        resources:
          requests:
            nvidia.com/gpu: 1
            cpu: 4000m
            memory: 16Gi
          limits:
            nvidia.com/gpu: 1
            cpu: 8000m
            memory: 32Gi
        
        # GPU-optimized environment
        env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        - name: NVIDIA_VISIBLE_DEVICES
          value: "all"
        - name: NVIDIA_DRIVER_CAPABILITIES
          value: "compute,utility"
        - name: CUDA_CACHE_DISABLE
          value: "0"
        - name: CUDA_CACHE_PATH
          value: "/tmp/cuda-cache"
        
        # Model optimization
        - name: BATCH_SIZE
          value: "16"
        - name: MODEL_PRECISION
          value: "fp16"          # Half precision for 2x performance
        - name: ENABLE_TENSORRT
          value: "true"          # TensorRT optimization
        - name: ENABLE_TORCH_JIT
          value: "true"          # JIT compilation
        
        # Memory optimization
        - name: PYTORCH_CUDA_ALLOC_CONF
          value: "max_split_size_mb:128"
        - name: CUDA_LAUNCH_BLOCKING
          value: "0"
        
        volumeMounts:
        - name: cuda-cache
          mountPath: /tmp/cuda-cache
        - name: model-cache
          mountPath: /app/models
      
      volumes:
      - name: cuda-cache
        emptyDir:
          sizeLimit: 5Gi
      - name: model-cache
        persistentVolumeClaim:
          claimName: model-cache-pvc
```

#### AI Model Optimization
```python
# ai_optimization.py
import torch
import torch.nn as nn
from torch.jit import script
import tensorrt as trt
import numpy as np
from typing import List, Tuple, Optional

class OptimizedAIProcessor:
    def __init__(self, model_path: str, device: str = "cuda"):
        self.device = torch.device(device)
        self.model = self._load_optimized_model(model_path)
        self.batch_size = 16
        self.input_queue = []
        
    def _load_optimized_model(self, model_path: str) -> nn.Module:
        """Load and optimize AI model for inference"""
        # Load model
        model = torch.load(model_path, map_location=self.device)
        model.eval()
        
        # Enable mixed precision
        model.half()
        
        # JIT compilation for optimization
        model = torch.jit.script(model)
        
        # TensorRT optimization (if available)
        if hasattr(torch.backends, 'cudnn'):
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.enabled = True
        
        return model
    
    @torch.no_grad()
    def process_batch(self, inputs: List[torch.Tensor]) -> List[torch.Tensor]:
        """Optimized batch processing"""
        # Ensure all inputs are on GPU
        gpu_inputs = [inp.to(self.device, non_blocking=True) for inp in inputs]
        
        # Stack into batch tensor
        batch_tensor = torch.stack(gpu_inputs)
        
        # Enable autocast for automatic mixed precision
        with torch.cuda.amp.autocast():
            outputs = self.model(batch_tensor)
        
        # Return individual results
        return list(torch.unbind(outputs, dim=0))
    
    def process_content(self, content_data: bytes) -> dict:
        """High-performance content processing"""
        # Preprocess on CPU while GPU is busy
        preprocessed = self._preprocess_async(content_data)
        
        # Add to batch queue
        self.input_queue.append(preprocessed)
        
        # Process when batch is full or timeout
        if len(self.input_queue) >= self.batch_size:
            return self._process_batch_queue()
        
        return self._process_single(preprocessed)
    
    def _preprocess_async(self, content_data: bytes) -> torch.Tensor:
        """Asynchronous preprocessing on CPU"""
        # Use CPU for preprocessing to free up GPU
        with torch.cuda.device(self.device):
            # Pin memory for faster GPU transfer
            tensor = torch.frombuffer(content_data, dtype=torch.uint8)
            tensor = tensor.pin_memory()
            return tensor
    
    def _process_batch_queue(self) -> List[dict]:
        """Process accumulated batch"""
        if not self.input_queue:
            return []
        
        # Process batch
        batch_results = self.process_batch(self.input_queue)
        
        # Clear queue
        processed_items = len(self.input_queue)
        self.input_queue.clear()
        
        # Convert to results
        results = []
        for i, result in enumerate(batch_results):
            results.append({
                'content_id': f'batch_{i}',
                'processing_time': self._get_processing_time(),
                'confidence': float(result.max()),
                'features': result.cpu().numpy().tolist()
            })
        
        return results

class TensorRTOptimizer:
    """TensorRT optimization for production inference"""
    
    def __init__(self, max_batch_size: int = 32):
        self.max_batch_size = max_batch_size
        self.logger = trt.Logger(trt.Logger.WARNING)
        
    def optimize_model(self, onnx_path: str, engine_path: str) -> bool:
        """Convert ONNX model to optimized TensorRT engine"""
        try:
            # Create builder and network
            builder = trt.Builder(self.logger)
            network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
            parser = trt.OnnxParser(network, self.logger)
            
            # Parse ONNX model
            with open(onnx_path, 'rb') as model:
                if not parser.parse(model.read()):
                    return False
            
            # Configure builder
            config = builder.create_builder_config()
            config.max_workspace_size = 1 << 30  # 1GB
            config.set_flag(trt.BuilderFlag.FP16)  # Enable FP16 precision
            
            # Set optimization profile
            profile = builder.create_optimization_profile()
            input_tensor = network.get_input(0)
            profile.set_shape(input_tensor.name, (1, 3, 224, 224), (8, 3, 224, 224), (32, 3, 224, 224))
            config.add_optimization_profile(profile)
            
            # Build engine
            engine = builder.build_engine(network, config)
            
            # Save engine
            with open(engine_path, 'wb') as f:
                f.write(engine.serialize())
            
            return True
            
        except Exception as e:
            print(f"TensorRT optimization failed: {e}")
            return False

# Model serving optimization
class ModelServer:
    def __init__(self, model_configs: dict):
        self.models = {}
        self.load_models(model_configs)
        
    def load_models(self, configs: dict):
        """Load multiple models with optimization"""
        for name, config in configs.items():
            processor = OptimizedAIProcessor(
                model_path=config['path'],
                device=config.get('device', 'cuda')
            )
            self.models[name] = processor
    
    async def process_request(self, model_name: str, content: bytes) -> dict:
        """Async request processing"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        processor = self.models[model_name]
        return processor.process_content(content)
```

---

## 🎨 Creator Economy Optimizations

### Upload Performance Optimization

#### Multi-Part Upload Optimization
```python
# upload_optimization.py
import asyncio
import aiohttp
import boto3
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import hashlib
import time

class OptimizedUploadManager:
    def __init__(self, aws_access_key: str, aws_secret_key: str, bucket: str):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            config=boto3.session.Config(
                max_pool_connections=50,  # Increase connection pool
                retries={'max_attempts': 3, 'mode': 'adaptive'},
                region_name='us-east-1'
            )
        )
        self.bucket = bucket
        self.chunk_size = 16 * 1024 * 1024  # 16MB chunks
        self.max_workers = 10
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
    
    async def upload_large_file(self, file_path: str, s3_key: str, 
                              metadata: dict = None) -> dict:
        """Optimized large file upload with multipart"""
        file_size = os.path.getsize(file_path)
        
        if file_size < self.chunk_size:
            return await self._simple_upload(file_path, s3_key, metadata)
        
        return await self._multipart_upload(file_path, s3_key, metadata)
    
    async def _multipart_upload(self, file_path: str, s3_key: str, 
                              metadata: dict = None) -> dict:
        """Optimized multipart upload"""
        start_time = time.time()
        
        # Initiate multipart upload
        response = self.s3_client.create_multipart_upload(
            Bucket=self.bucket,
            Key=s3_key,
            Metadata=metadata or {},
            StorageClass='STANDARD_IA',  # Cost-optimized storage
            ServerSideEncryption='AES256'
        )
        upload_id = response['UploadId']
        
        try:
            # Calculate parts
            file_size = os.path.getsize(file_path)
            parts_count = (file_size + self.chunk_size - 1) // self.chunk_size
            
            # Upload parts concurrently
            upload_tasks = []
            for part_num in range(1, parts_count + 1):
                task = self._upload_part(
                    file_path, s3_key, upload_id, part_num, file_size
                )
                upload_tasks.append(task)
            
            # Wait for all parts to complete
            parts = await asyncio.gather(*upload_tasks)
            
            # Complete multipart upload
            parts_list = [
                {'ETag': part['etag'], 'PartNumber': part['part_number']}
                for part in sorted(parts, key=lambda x: x['part_number'])
            ]
            
            complete_response = self.s3_client.complete_multipart_upload(
                Bucket=self.bucket,
                Key=s3_key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts_list}
            )
            
            upload_time = time.time() - start_time
            throughput = file_size / upload_time / (1024 * 1024)  # MB/s
            
            return {
                'success': True,
                'location': complete_response['Location'],
                'etag': complete_response['ETag'],
                'upload_time': upload_time,
                'throughput_mbps': throughput,
                'file_size': file_size,
                'parts_count': parts_count
            }
            
        except Exception as e:
            # Abort multipart upload on failure
            self.s3_client.abort_multipart_upload(
                Bucket=self.bucket,
                Key=s3_key,
                UploadId=upload_id
            )
            raise e
    
    async def _upload_part(self, file_path: str, s3_key: str, upload_id: str,
                          part_number: int, total_size: int) -> dict:
        """Upload single part asynchronously"""
        start_byte = (part_number - 1) * self.chunk_size
        end_byte = min(start_byte + self.chunk_size, total_size)
        
        # Read part data
        loop = asyncio.get_event_loop()
        part_data = await loop.run_in_executor(
            self.executor,
            self._read_file_chunk,
            file_path, start_byte, end_byte - start_byte
        )
        
        # Upload part
        response = await loop.run_in_executor(
            self.executor,
            self._upload_part_sync,
            part_data, s3_key, upload_id, part_number
        )
        
        return {
            'part_number': part_number,
            'etag': response['ETag'],
            'size': len(part_data)
        }
    
    def _read_file_chunk(self, file_path: str, start: int, size: int) -> bytes:
        """Read file chunk synchronously"""
        with open(file_path, 'rb') as f:
            f.seek(start)
            return f.read(size)
    
    def _upload_part_sync(self, data: bytes, s3_key: str, upload_id: str,
                         part_number: int) -> dict:
        """Upload part synchronously"""
        return self.s3_client.upload_part(
            Bucket=self.bucket,
            Key=s3_key,
            PartNumber=part_number,
            UploadId=upload_id,
            Body=data
        )

class CreatorContentProcessor:
    """Optimized content processing for creators"""
    
    def __init__(self):
        self.upload_manager = OptimizedUploadManager(
            aws_access_key=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_key=os.getenv('AWS_SECRET_KEY'),
            bucket='ainflue-creator-content'
        )
        self.processing_queue = asyncio.Queue(maxsize=100)
        self.workers = []
    
    async def start_workers(self, num_workers: int = 5):
        """Start processing workers"""
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
    
    async def _worker(self, worker_name: str):
        """Content processing worker"""
        while True:
            try:
                # Get content from queue
                content_item = await self.processing_queue.get()
                
                if content_item is None:  # Shutdown signal
                    break
                
                # Process content
                await self._process_content_item(content_item, worker_name)
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except Exception as e:
                print(f"Worker {worker_name} error: {e}")
    
    async def _process_content_item(self, item: dict, worker_name: str):
        """Process individual content item"""
        start_time = time.time()
        
        try:
            # Extract metadata
            content_type = item['content_type']
            file_path = item['file_path']
            creator_id = item['creator_id']
            
            # Generate optimized S3 key
            s3_key = self._generate_s3_key(creator_id, content_type, file_path)
            
            # Prepare metadata
            metadata = {
                'creator-id': creator_id,
                'content-type': content_type,
                'upload-timestamp': str(int(time.time())),
                'processed-by': worker_name
            }
            
            # Upload to S3
            upload_result = await self.upload_manager.upload_large_file(
                file_path, s3_key, metadata
            )
            
            # Update database
            await self._update_content_status(
                item['content_id'], 
                'uploaded', 
                upload_result
            )
            
            # Trigger AI processing
            await self._trigger_ai_processing(item['content_id'], s3_key)
            
            processing_time = time.time() - start_time
            print(f"Processed {item['content_id']} in {processing_time:.2f}s")
            
        except Exception as e:
            await self._update_content_status(
                item['content_id'], 
                'failed', 
                {'error': str(e)}
            )
            raise e
    
    def _generate_s3_key(self, creator_id: str, content_type: str, 
                        file_path: str) -> str:
        """Generate optimized S3 key for performance"""
        # Use creator ID prefix for S3 request distribution
        creator_prefix = hashlib.md5(creator_id.encode()).hexdigest()[:2]
        
        # Add timestamp for versioning
        timestamp = int(time.time())
        
        # Extract file extension
        file_ext = os.path.splitext(file_path)[1]
        
        return f"{creator_prefix}/{creator_id}/{content_type}/{timestamp}{file_ext}"
