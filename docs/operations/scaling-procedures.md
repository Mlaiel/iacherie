# 📈 Ainflue Platform - Scaling Procedures & Thresholds

## 📋 Overview

This document provides precise scaling procedures and thresholds for the Ainflue platform. All thresholds are based on production metrics and performance testing to ensure optimal resource utilization and performance.

## 🎯 Scaling Strategy

### Horizontal Scaling (Adding Instances)
- **Primary Method**: For stateless services
- **Trigger Time**: 30-60 seconds
- **Cost Impact**: Linear scaling cost
- **Use Cases**: API gateways, web servers, AI processing

### Vertical Scaling (Increasing Resources)
- **Primary Method**: For stateful services
- **Trigger Time**: 2-5 minutes (requires restart)
- **Cost Impact**: Higher per-unit cost
- **Use Cases**: Databases, Redis, file storage

### Auto Scaling (Kubernetes HPA/VPA)
- **Primary Method**: For predictable workloads
- **Trigger Time**: 15-30 seconds
- **Cost Impact**: Optimized resource usage
- **Use Cases**: Web traffic, batch processing

## 🔢 Precise Scaling Thresholds

### CPU-Based Scaling

#### API Gateway Service
```yaml
scaling_thresholds:
  cpu_utilization:
    scale_up:
      threshold: 70%
      duration: 2 minutes
      action: "Add 1 replica (max 10)"
      cooldown: 3 minutes
    
    scale_down:
      threshold: 30%
      duration: 5 minutes
      action: "Remove 1 replica (min 2)"
      cooldown: 10 minutes
    
    emergency_scale:
      threshold: 90%
      duration: 30 seconds
      action: "Add 3 replicas immediately"
      max_replicas: 15
```

#### AI Processing Engine
```yaml
scaling_thresholds:
  cpu_utilization:
    scale_up:
      threshold: 80%
      duration: 3 minutes
      action: "Add 1 replica (max 8)"
      cooldown: 5 minutes
    
    scale_down:
      threshold: 40%
      duration: 10 minutes
      action: "Remove 1 replica (min 1)"
      cooldown: 15 minutes
    
  queue_length:
    scale_up:
      threshold: 50 items
      duration: 1 minute
      action: "Add 2 replicas"
      max_replicas: 12
```

#### Content Processing Workers
```yaml
scaling_thresholds:
  queue_depth:
    scale_up:
      threshold: 100 jobs
      duration: 30 seconds
      action: "Add 2 workers (max 20)"
      cooldown: 2 minutes
    
    scale_down:
      threshold: 10 jobs
      duration: 5 minutes
      action: "Remove 1 worker (min 3)"
      cooldown: 8 minutes
    
  processing_time:
    scale_up:
      threshold: 300 seconds avg
      duration: 2 minutes
      action: "Add 1 worker"
      priority: "high"
```

### Memory-Based Scaling

#### Database Connections
```yaml
scaling_thresholds:
  memory_utilization:
    scale_up:
      threshold: 85%
      duration: 2 minutes
      action: "Increase memory limit +1GB"
      max_memory: "16GB"
    
    scale_down:
      threshold: 50%
      duration: 30 minutes
      action: "Decrease memory limit -1GB"
      min_memory: "4GB"
    
  connection_pool:
    expand:
      threshold: 80% pool usage
      action: "Increase pool size +20"
      max_connections: 200
```

#### Redis Cache
```yaml
scaling_thresholds:
  memory_usage:
    scale_up:
      threshold: 80%
      duration: 5 minutes
      action: "Add memory +2GB or add replica"
      strategy: "vertical_then_horizontal"
    
  cache_hit_ratio:
    optimize:
      threshold: 85% (below)
      action: "Increase TTL, add cache warmup"
      target_ratio: 95%
```

### Request-Based Scaling

#### API Response Times
```yaml
scaling_thresholds:
  response_time:
    p95_latency:
      threshold: 2000ms
      duration: 1 minute
      action: "Scale up API pods +2"
      target_latency: 500ms
    
    p99_latency:
      threshold: 5000ms
      duration: 30 seconds
      action: "Emergency scale +3 pods"
      investigate: true
    
  requests_per_second:
    scale_up:
      threshold: 1000 RPS
      action: "Add 1 replica per 500 RPS"
      max_rps_per_pod: 500
```

#### Database Query Performance
```yaml
scaling_thresholds:
  query_performance:
    slow_queries:
      threshold: 5 queries > 1s in 1 minute
      action: "Add read replica"
      optimize: "Review query plans"
    
    connection_wait:
      threshold: 100ms avg wait time
      action: "Increase connection pool +10"
      max_pool_size: 100
```

## 🚀 Automated Scaling Implementation

### Kubernetes Horizontal Pod Autoscaler (HPA)

#### API Gateway HPA
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "500"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 180
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

#### AI Engine HPA
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-engine-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-engine
  minReplicas: 1
  maxReplicas: 8
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
  - type: External
    external:
      metric:
        name: redis_queue_length
        selector:
          matchLabels:
            queue: "ai-processing"
      target:
        type: AverageValue
        averageValue: "50"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 2
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 600
      policies:
      - type: Pods
        value: 1
        periodSeconds: 120
```

### Vertical Pod Autoscaler (VPA)

#### Database VPA
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: postgresql-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: StatefulSet
    name: postgresql
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: postgresql
      minAllowed:
        cpu: 500m
        memory: 2Gi
      maxAllowed:
        cpu: 4000m
        memory: 16Gi
      controlledResources: ["cpu", "memory"]
      controlledValues: RequestsAndLimits
```

## 📊 Custom Scaling Metrics

### Redis Queue Depth Metric
```python
# metrics/queue_metrics.py
from prometheus_client import Gauge
import redis

queue_depth_gauge = Gauge('redis_queue_depth', 'Number of items in queue', ['queue_name'])

def collect_queue_metrics():
    r = redis.Redis(host='redis', port=6379)
    
    queues = ['ai-processing', 'content-analysis', 'notifications']
    for queue in queues:
        depth = r.llen(queue)
        queue_depth_gauge.labels(queue_name=queue).set(depth)
```

### Database Connection Pool Metric
```python
# metrics/db_metrics.py
from prometheus_client import Gauge
import psycopg2

connection_pool_gauge = Gauge('db_connection_pool_usage', 'Database connection pool usage')
connection_wait_gauge = Gauge('db_connection_wait_time', 'Database connection wait time')

def collect_db_metrics():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    with conn.cursor() as cur:
        # Get connection pool usage
        cur.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active';")
        active_connections = cur.fetchone()[0]
        
        cur.execute("SHOW max_connections;")
        max_connections = cur.fetchone()[0]
        
        usage_percent = (active_connections / max_connections) * 100
        connection_pool_gauge.set(usage_percent)
```

### API Response Time Percentiles
```python
# metrics/api_metrics.py
from prometheus_client import Histogram
import time

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'status_code'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

def track_request_duration(method, endpoint, status_code, duration):
    request_duration.labels(
        method=method,
        endpoint=endpoint,
        status_code=status_code
    ).observe(duration)
```

## 🎛️ Manual Scaling Procedures

### Emergency Manual Scaling

#### Immediate Scale-Up (1-2 minutes)
```bash
#!/bin/bash
# emergency-scale-up.sh

echo "🚨 Emergency scaling initiated"

# Scale critical services immediately
kubectl scale deployment api-gateway --replicas=8
kubectl scale deployment ai-engine --replicas=5
kubectl scale deployment content-processor --replicas=10

# Monitor scaling progress
kubectl get pods -l app=api-gateway -w &
kubectl get pods -l app=ai-engine -w &

# Check resource usage
kubectl top nodes
kubectl top pods

echo "✅ Emergency scaling completed"
```

#### Gradual Scale-Down (5-10 minutes)
```bash
#!/bin/bash
# gradual-scale-down.sh

echo "📉 Gradual scale-down initiated"

# Scale down non-critical services first
kubectl scale deployment content-processor --replicas=3
sleep 120

# Scale down API services
kubectl scale deployment api-gateway --replicas=3
sleep 180

# Scale down AI engine
kubectl scale deployment ai-engine --replicas=2

# Verify system stability
./scripts/health-check.sh

echo "✅ Gradual scale-down completed"
```

### Planned Scaling for Events

#### Pre-Event Scaling (30 minutes before)
```bash
#!/bin/bash
# pre-event-scaling.sh

EVENT_TYPE=${1:-"normal"}  # normal, high, extreme
EVENT_DURATION=${2:-60}   # minutes

case $EVENT_TYPE in
  "normal")
    API_REPLICAS=5
    AI_REPLICAS=3
    WORKER_REPLICAS=8
    ;;
  "high")
    API_REPLICAS=8
    AI_REPLICAS=5
    WORKER_REPLICAS=12
    ;;
  "extreme")
    API_REPLICAS=12
    AI_REPLICAS=8
    WORKER_REPLICAS=20
    ;;
esac

echo "🎯 Pre-event scaling for $EVENT_TYPE traffic"

# Pre-warm services
kubectl scale deployment api-gateway --replicas=$API_REPLICAS
kubectl scale deployment ai-engine --replicas=$AI_REPLICAS
kubectl scale deployment content-processor --replicas=$WORKER_REPLICAS

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=api-gateway --timeout=300s
kubectl wait --for=condition=ready pod -l app=ai-engine --timeout=300s

# Pre-warm caches
curl -X POST http://localhost/api/v1/cache/warmup

# Schedule post-event scale-down
echo "kubectl scale deployment api-gateway --replicas=2" | at now + $EVENT_DURATION minutes
echo "kubectl scale deployment ai-engine --replicas=1" | at now + $EVENT_DURATION minutes
echo "kubectl scale deployment content-processor --replicas=3" | at now + $EVENT_DURATION minutes

echo "✅ Pre-event scaling completed"
```

## 📈 Predictive Scaling

### Time-Based Scaling Patterns

#### Daily Pattern Scaling
```yaml
# k8s/cronjob-morning-scale.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: morning-scale-up
spec:
  schedule: "0 8 * * 1-5"  # 8 AM weekdays
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: scaler
            image: bitnami/kubectl
            command:
            - /bin/sh
            - -c
            - |
              kubectl scale deployment api-gateway --replicas=5
              kubectl scale deployment ai-engine --replicas=3
              kubectl scale deployment content-processor --replicas=8
          restartPolicy: OnFailure
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: evening-scale-down
spec:
  schedule: "0 22 * * *"  # 10 PM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: scaler
            image: bitnami/kubectl
            command:
            - /bin/sh
            - -c
            - |
              kubectl scale deployment api-gateway --replicas=2
              kubectl scale deployment ai-engine --replicas=1
              kubectl scale deployment content-processor --replicas=3
          restartPolicy: OnFailure
```

#### Weekend Pattern Scaling
```yaml
# k8s/cronjob-weekend-scale.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: weekend-scale-down
spec:
  schedule: "0 0 * * 6"  # Saturday midnight
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: scaler
            image: bitnami/kubectl
            command:
            - /bin/sh
            - -c
            - |
              kubectl scale deployment api-gateway --replicas=1
              kubectl scale deployment ai-engine --replicas=1
              kubectl scale deployment content-processor --replicas=2
          restartPolicy: OnFailure
```

### Machine Learning-Based Scaling

#### Predictive Scaling Script
```python
# scripts/predictive_scaling.py
import numpy as np
from sklearn.linear_model import LinearRegression
from prometheus_api_client import PrometheusConnect
import kubernetes
from datetime import datetime, timedelta

class PredictiveScaler:
    def __init__(self):
        self.prometheus = PrometheusConnect(url="http://prometheus:9090")
        kubernetes.config.load_incluster_config()
        self.k8s_apps = kubernetes.client.AppsV1Api()
    
    def get_historical_metrics(self, metric_name, hours=168):  # 1 week
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        query = f'{metric_name}[{hours}h]'
        result = self.prometheus.custom_query_range(
            query=query,
            start_time=start_time,
            end_time=end_time,
            step=3600  # 1 hour steps
        )
        
        return [(float(point[1]), point[0]) for point in result[0]['values']]
    
    def predict_load(self, historical_data):
        # Prepare features: hour of day, day of week, trend
        X = []
        y = []
        
        for i, (value, timestamp) in enumerate(historical_data):
            dt = datetime.fromtimestamp(timestamp)
            features = [
                dt.hour,  # Hour of day
                dt.weekday(),  # Day of week
                i,  # Trend component
                np.sin(2 * np.pi * dt.hour / 24),  # Hourly cycle
                np.sin(2 * np.pi * dt.weekday() / 7)  # Weekly cycle
            ]
            X.append(features)
            y.append(value)
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next hour
        next_hour = datetime.now() + timedelta(hours=1)
        next_features = [
            next_hour.hour,
            next_hour.weekday(),
            len(historical_data),
            np.sin(2 * np.pi * next_hour.hour / 24),
            np.sin(2 * np.pi * next_hour.weekday() / 7)
        ]
        
        prediction = model.predict([next_features])[0]
        return max(1, int(prediction))
    
    def scale_deployment(self, deployment_name, namespace, replicas):
        try:
            # Get current deployment
            deployment = self.k8s_apps.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # Update replica count
            deployment.spec.replicas = replicas
            
            # Apply changes
            self.k8s_apps.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )
            
            print(f"Scaled {deployment_name} to {replicas} replicas")
            return True
            
        except Exception as e:
            print(f"Error scaling {deployment_name}: {e}")
            return False
    
    def run_predictive_scaling(self):
        # Get historical CPU usage
        cpu_data = self.get_historical_metrics('cpu_usage_percent')
        
        # Predict required capacity
        predicted_cpu = self.predict_load(cpu_data)
        
        # Calculate required replicas (target 70% CPU usage)
        current_replicas = 2  # Get from Kubernetes
        required_replicas = max(1, int(current_replicas * predicted_cpu / 70))
        
        # Apply scaling with safety limits
        max_replicas = 10
        min_replicas = 1
        
        safe_replicas = max(min_replicas, min(max_replicas, required_replicas))
        
        # Scale if significant change needed
        if abs(safe_replicas - current_replicas) >= 1:
            self.scale_deployment('api-gateway', 'default', safe_replicas)

if __name__ == "__main__":
    scaler = PredictiveScaler()
    scaler.run_predictive_scaling()
```

## 🔄 Database Scaling Procedures

### PostgreSQL Read Replica Scaling

#### Automatic Read Replica Creation
```bash
#!/bin/bash
# create-read-replica.sh

MASTER_HOST="postgresql-master"
REPLICA_NAME="postgresql-replica-$(date +%s)"

echo "Creating read replica: $REPLICA_NAME"

# Create replica configuration
cat > replica-config.yaml << EOF
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: $REPLICA_NAME
spec:
  serviceName: $REPLICA_NAME
  replicas: 1
  template:
    spec:
      containers:
      - name: postgresql
        image: postgres:14
        env:
        - name: POSTGRES_USER
          value: "replica"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: PGUSER
          value: "replica"
        command:
        - /bin/bash
        - -c
        - |
          pg_basebackup -h $MASTER_HOST -U replication -D /var/lib/postgresql/data -W -v -P -R
          postgres
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi
EOF

kubectl apply -f replica-config.yaml

# Wait for replica to be ready
kubectl wait --for=condition=ready pod -l app=$REPLICA_NAME --timeout=600s

# Update load balancer to include replica
kubectl patch configmap postgres-config \
  --patch '{"data":{"replicas":"'$MASTER_HOST','$REPLICA_NAME'"}}'

echo "✅ Read replica $REPLICA_NAME created and configured"
```

### MongoDB Sharding

#### Add Shard Procedure
```bash
#!/bin/bash
# add-mongodb-shard.sh

SHARD_NAME="shard$(date +%s)"
SHARD_REPLICAS=3

echo "Adding MongoDB shard: $SHARD_NAME"

# Deploy shard replica set
for i in $(seq 1 $SHARD_REPLICAS); do
  kubectl apply -f - << EOF
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: $SHARD_NAME-$i
spec:
  serviceName: $SHARD_NAME-$i
  replicas: 1
  template:
    spec:
      containers:
      - name: mongodb
        image: mongo:5.0
        command:
        - mongod
        - --shardsvr
        - --replSet
        - $SHARD_NAME
        - --port
        - "27017"
        ports:
        - containerPort: 27017
        volumeMounts:
        - name: data
          mountPath: /data/db
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi
EOF
done

# Wait for shard pods to be ready
kubectl wait --for=condition=ready pod -l app=$SHARD_NAME --timeout=600s

# Initialize replica set
kubectl exec -it $SHARD_NAME-1-0 -- mongo --eval "
rs.initiate({
  _id: '$SHARD_NAME',
  members: [
    {_id: 0, host: '$SHARD_NAME-1:27017'},
    {_id: 1, host: '$SHARD_NAME-2:27017'},
    {_id: 2, host: '$SHARD_NAME-3:27017'}
  ]
})
"

# Add shard to cluster
kubectl exec -it mongos-0 -- mongo --eval "
sh.addShard('$SHARD_NAME/$SHARD_NAME-1:27017,$SHARD_NAME-2:27017,$SHARD_NAME-3:27017')
"

echo "✅ MongoDB shard $SHARD_NAME added successfully"
```

## 📊 Monitoring Scaling Performance

### Scaling Metrics Dashboard

#### Prometheus Queries for Scaling Metrics
```yaml
# Scaling event frequency
scaling_events_per_hour:
  query: increase(kube_deployment_status_replicas[1h])

# Scaling effectiveness
scaling_effectiveness:
  query: rate(http_requests_total[5m]) / kube_deployment_status_replicas

# Resource utilization after scaling
resource_utilization_post_scale:
  query: avg_over_time(container_cpu_usage_seconds_total[10m]) / container_spec_cpu_quota

# Scaling latency
scaling_latency:
  query: histogram_quantile(0.95, scaling_duration_seconds_bucket)
```

#### Grafana Dashboard Configuration
```json
{
  "dashboard": {
    "title": "Scaling Performance Dashboard",
    "panels": [
      {
        "title": "Replica Count Over Time",
        "type": "graph",
        "targets": [
          {
            "expr": "kube_deployment_status_replicas{deployment=\"api-gateway\"}",
            "legendFormat": "API Gateway Replicas"
          }
        ]
      },
      {
        "title": "Scaling Events",
        "type": "stat",
        "targets": [
          {
            "expr": "increase(hpa_scaling_events_total[1h])",
            "legendFormat": "Scaling Events/Hour"
          }
        ]
      },
      {
        "title": "CPU Usage vs Replicas",
        "type": "graph",
        "targets": [
          {
            "expr": "avg(rate(container_cpu_usage_seconds_total[5m])) * 100",
            "legendFormat": "CPU Usage %"
          },
          {
            "expr": "kube_deployment_status_replicas * 10",
            "legendFormat": "Replicas (x10)"
          }
        ]
      }
    ]
  }
}
```

### Scaling Alerts

#### HPA Scaling Alerts
```yaml
# prometheus/scaling_alerts.yml
groups:
- name: scaling_alerts
  rules:
  - alert: FrequentScaling
    expr: increase(hpa_scaling_events_total[15m]) > 5
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "HPA scaling too frequently"
      description: "HPA {{ $labels.hpa }} has scaled {{ $value }} times in 15 minutes"
  
  - alert: ScalingAtMaxReplicas
    expr: kube_deployment_status_replicas == kube_hpa_spec_max_replicas
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Deployment at maximum replicas"
      description: "Deployment {{ $labels.deployment }} is at maximum replica count"
  
  - alert: ScalingFailed
    expr: increase(hpa_scaling_failures_total[5m]) > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "HPA scaling failed"
      description: "HPA {{ $labels.hpa }} failed to scale: {{ $labels.reason }}"
```

## 🎯 Cost Optimization

### Cost-Aware Scaling

#### Instance Type Optimization
```python
# scripts/cost_optimized_scaling.py
import boto3
from kubernetes import client, config

class CostOptimizedScaler:
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        config.load_incluster_config()
        self.k8s = client.CoreV1Api()
    
    def get_instance_costs(self):
        # Get current spot prices
        response = self.ec2.describe_spot_price_history(
            InstanceTypes=['t3.medium', 't3.large', 't3.xlarge'],
            ProductDescriptions=['Linux/UNIX'],
            MaxResults=10
        )
        
        costs = {}
        for price in response['SpotPrices']:
            instance_type = price['InstanceType']
            costs[instance_type] = float(price['SpotPrice'])
        
        return costs
    
    def recommend_instance_mix(self, required_cpu, required_memory):
        costs = self.get_instance_costs()
        
        # Instance specifications (vCPU, Memory GB, Cost per hour)
        instances = {
            't3.medium': (2, 4, costs.get('t3.medium', 0.05)),
            't3.large': (2, 8, costs.get('t3.large', 0.10)),
            't3.xlarge': (4, 16, costs.get('t3.xlarge', 0.20))
        }
        
        # Find most cost-effective combination
        best_cost = float('inf')
        best_mix = None
        
        for combo in self.generate_combinations(instances, required_cpu, required_memory):
            total_cost = sum(instances[inst][2] * count for inst, count in combo.items())
            if total_cost < best_cost:
                best_cost = total_cost
                best_mix = combo
        
        return best_mix, best_cost
    
    def scale_with_cost_optimization(self, deployment_name, target_replicas):
        # Calculate resource requirements
        required_cpu = target_replicas * 0.5  # 500m per replica
        required_memory = target_replicas * 1  # 1GB per replica
        
        # Get cost-optimized instance mix
        instance_mix, cost = self.recommend_instance_mix(required_cpu, required_memory)
        
        print(f"Recommended instance mix: {instance_mix}")
        print(f"Estimated hourly cost: ${cost:.2f}")
        
        # Apply scaling with node affinity for cost optimization
        self.apply_cost_optimized_deployment(deployment_name, target_replicas, instance_mix)
```

### Spot Instance Integration
```yaml
# k8s/spot-instance-nodepool.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: spot-instance-config
data:
  nodepool.yaml: |
    apiVersion: kops.k8s.io/v1alpha2
    kind: InstanceGroup
    metadata:
      name: spot-nodes
    spec:
      image: 099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210415
      instanceMetadata:
        httpTokens: required
      machineType: t3.large
      maxSize: 20
      minSize: 0
      mixedInstancesPolicy:
        instances:
        - t3.large
        - t3.xlarge
        - m5.large
        onDemandAboveBase: 0
        onDemandBase: 0
        spotAllocationStrategy: diversified
        spotInstancePools: 3
      nodeLabels:
        node-type: spot
        cost-optimization: enabled
      role: Node
      subnets:
      - us-west-2a
      - us-west-2b
      taints:
      - spot-instance:NoSchedule
```

## 📋 Scaling Runbook Checklist

### Pre-Scaling Checklist
- [ ] Monitor current resource utilization
- [ ] Check application health status
- [ ] Verify auto-scaling policies are active
- [ ] Confirm cost budgets and limits
- [ ] Check dependency service capacity
- [ ] Validate network bandwidth availability
- [ ] Review recent scaling events

### During Scaling Checklist
- [ ] Monitor pod creation/termination
- [ ] Watch for resource constraints
- [ ] Check service discovery updates
- [ ] Monitor application performance metrics
- [ ] Verify load balancer health
- [ ] Check database connection pools
- [ ] Monitor error rates and latency

### Post-Scaling Checklist
- [ ] Verify all pods are healthy
- [ ] Confirm performance improvements
- [ ] Check cost impact
- [ ] Update capacity planning docs
- [ ] Review scaling effectiveness
- [ ] Document lessons learned
- [ ] Update alert thresholds if needed

---

**Document Information**
- **Version**: 1.0.0
- **Last Updated**: 2024-01-15
- **Next Review**: 2024-04-15
- **Owner**: Platform Engineering Team
- **Approved By**: CTO

---

> **Important**: These scaling procedures are based on production data and performance testing. Always test scaling procedures in staging environments before applying to production systems.