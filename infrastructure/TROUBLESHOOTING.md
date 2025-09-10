# 🔧 Ainflue Infrastructure Troubleshooting Guide

**Author:** Fahed Mlaiel <mlaiel@live.de>  
**Team:** DevOps Engineer + SRE Expert + Infrastructure Specialist  
**Version:** 1.0.0  
**Last Updated:** January 2025  

## 📋 Table of Contents

1. [Emergency Response Procedures](#emergency-response-procedures)
2. [Common Issues and Solutions](#common-issues-and-solutions)
3. [Kubernetes Troubleshooting](#kubernetes-troubleshooting)
4. [Database Issues](#database-issues)
5. [Network and Connectivity](#network-and-connectivity)
6. [Performance Issues](#performance-issues)
7. [Security Incidents](#security-incidents)
8. [Creator Economy Specific Issues](#creator-economy-specific-issues)

---

## 🚨 Emergency Response Procedures

### Critical Incident Response Workflow

#### Platform Down (P0 - Critical)
```bash
# IMMEDIATE ACTIONS (First 5 minutes)
# 1. Acknowledge the incident
echo "INCIDENT: Platform Down - $(date)" >> /var/log/incidents.log

# 2. Check overall platform health
kubectl get nodes
kubectl get pods --all-namespaces | grep -v Running

# 3. Check load balancer and ingress
kubectl get ingress -n ainflue
kubectl describe ingress ainflue-ingress -n ainflue

# 4. Check external dependencies
curl -I https://api.ainflue.com/health
dig api.ainflue.com

# 5. Notify incident commander
curl -X POST https://hooks.slack.com/webhook/incident \
  -d '{"text":"🚨 P0 INCIDENT: Platform Down - Immediate response required"}'
```

#### Response Escalation Matrix
```yaml
Escalation_Levels:
  Level_1_Response: # 0-15 minutes
    Team: On-call DevOps Engineer
    Actions:
      - Initial assessment and triage
      - Implement immediate containment
      - Gather diagnostic information
      - Notify Level 2 if unresolved
    
  Level_2_Response: # 15-60 minutes
    Team: Senior Infrastructure Engineer + Team Lead
    Actions:
      - Deep technical investigation
      - Coordinate with multiple teams
      - Implement complex fixes
      - Notify Level 3 if unresolved
    
  Level_3_Response: # 60+ minutes
    Team: CTO + Infrastructure Architect + External Experts
    Actions:
      - Strategic decision making
      - Resource allocation
      - External vendor coordination
      - Customer communication
```

### Emergency Runbooks

#### Database Outage Response
```bash
#!/bin/bash
# database-outage-response.sh

echo "=== DATABASE OUTAGE RESPONSE RUNBOOK ==="
echo "Started at: $(date)"

# Step 1: Check database connectivity
echo "1. Checking database connectivity..."
kubectl exec -n ainflue deployment/ainflue-api -- pg_isready -h $DB_HOST -p 5432 -U $DB_USER

# Step 2: Check database status
echo "2. Checking RDS instance status..."
aws rds describe-db-instances --db-instance-identifier ainflue-prod-postgres \
  --query 'DBInstances[0].DBInstanceStatus'

# Step 3: Check for read replicas
echo "3. Checking read replica status..."
aws rds describe-db-instances --query 'DBInstances[?DBInstanceIdentifier==`ainflue-prod-postgres-replica`]'

# Step 4: Check recent CloudWatch metrics
echo "4. Checking database metrics..."
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=ainflue-prod-postgres \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average

# Step 5: Emergency failover to replica (if needed)
if [ "$1" == "failover" ]; then
    echo "5. EMERGENCY: Promoting read replica to primary..."
    aws rds promote-read-replica --db-instance-identifier ainflue-prod-postgres-replica
    echo "Updating application configuration..."
    kubectl patch configmap ainflue-config -n ainflue -p '{"data":{"DATABASE_HOST":"ainflue-prod-postgres-replica.region.rds.amazonaws.com"}}'
    kubectl rollout restart deployment/ainflue-api -n ainflue
fi

echo "=== DATABASE OUTAGE RESPONSE COMPLETED ==="
```

#### API Service Recovery
```bash
#!/bin/bash
# api-service-recovery.sh

echo "=== API SERVICE RECOVERY RUNBOOK ==="

# Step 1: Check pod status
echo "1. Checking API pod status..."
kubectl get pods -n ainflue -l app=ainflue-api

# Step 2: Check recent pod logs
echo "2. Checking recent pod logs..."
kubectl logs -n ainflue -l app=ainflue-api --tail=100 --timestamps

# Step 3: Check resource usage
echo "3. Checking resource usage..."
kubectl top pods -n ainflue -l app=ainflue-api

# Step 4: Check service endpoints
echo "4. Checking service endpoints..."
kubectl get endpoints -n ainflue ainflue-api-service

# Step 5: Emergency restart if needed
if [ "$1" == "restart" ]; then
    echo "5. EMERGENCY: Restarting API deployment..."
    kubectl rollout restart deployment/ainflue-api -n ainflue
    kubectl rollout status deployment/ainflue-api -n ainflue --timeout=300s
fi

# Step 6: Scale up for immediate recovery
if [ "$1" == "scale" ]; then
    echo "6. EMERGENCY: Scaling up API pods..."
    kubectl scale deployment ainflue-api --replicas=10 -n ainflue
    kubectl rollout status deployment/ainflue-api -n ainflue --timeout=300s
fi

echo "=== API SERVICE RECOVERY COMPLETED ==="
```

---

## 🔍 Common Issues and Solutions

### Application Issues

#### High Error Rate (5xx Errors)
```bash
# Diagnosis
echo "=== DIAGNOSING HIGH ERROR RATE ==="

# Check current error rate
kubectl exec -n monitoring prometheus-server-0 -- promtool query instant \
  'rate(ainflue_api_requests_total{status=~"5.."}[5m]) / rate(ainflue_api_requests_total[5m]) * 100'

# Check which endpoints are failing
kubectl logs -n ainflue -l app=ainflue-api --since=10m | grep "ERROR\|5[0-9][0-9]" | head -20

# Check pod health
kubectl get pods -n ainflue -l app=ainflue-api -o wide

# Common Solutions:
# 1. Memory issues
kubectl describe pods -n ainflue -l app=ainflue-api | grep -A 5 "Memory"

# 2. Database connection issues
kubectl exec -n ainflue deployment/ainflue-api -- netstat -an | grep 5432

# 3. Restart unhealthy pods
kubectl delete pods -n ainflue -l app=ainflue-api --field-selector=status.phase!=Running

# 4. Check dependencies
kubectl get pods -n ainflue | grep -E "(redis|postgres|elasticsearch)"
```

#### Memory Leaks and OOM Kills
```bash
# Diagnosis
echo "=== DIAGNOSING MEMORY ISSUES ==="

# Check OOMKilled pods
kubectl get pods -n ainflue --field-selector=status.phase=Failed -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].lastState.terminated.reason}{"\n"}{end}' | grep OOMKilled

# Check current memory usage
kubectl top pods -n ainflue -l app=ainflue-api --sort-by=memory

# Check memory limits and requests
kubectl describe deployment ainflue-api -n ainflue | grep -A 5 -B 5 "Limits\|Requests"

# Solutions:
# 1. Increase memory limits
kubectl patch deployment ainflue-api -n ainflue -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","resources":{"limits":{"memory":"2Gi"}}}]}}}}'

# 2. Check for memory leaks in logs
kubectl logs -n ainflue -l app=ainflue-api --since=1h | grep -i "memory\|heap\|gc"

# 3. Enable memory profiling
kubectl exec -n ainflue deployment/ainflue-api -- curl http://localhost:6060/debug/pprof/heap > heap.prof

# 4. Restart pods with memory issues
kubectl get pods -n ainflue -l app=ainflue-api -o json | jq -r '.items[] | select(.status.containerStatuses[0].restartCount > 5) | .metadata.name' | xargs kubectl delete pod -n ainflue
```

#### Slow API Response Times
```bash
# Diagnosis
echo "=== DIAGNOSING SLOW API RESPONSE ==="

# Check current latency metrics
kubectl exec -n monitoring prometheus-server-0 -- promtool query instant \
  'histogram_quantile(0.95, rate(ainflue_api_request_duration_seconds_bucket[5m])) * 1000'

# Check database query performance
kubectl exec -n ainflue deployment/ainflue-api -- psql $DATABASE_URL -c "
SELECT query, mean_time, rows, 100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Check CPU throttling
kubectl top pods -n ainflue -l app=ainflue-api --sort-by=cpu

# Solutions:
# 1. Scale horizontally
kubectl scale deployment ainflue-api --replicas=5 -n ainflue

# 2. Optimize database queries
kubectl exec -n ainflue deployment/ainflue-api -- psql $DATABASE_URL -c "
EXPLAIN ANALYZE SELECT * FROM uploads WHERE created_at > NOW() - INTERVAL '1 hour';"

# 3. Add database indices
kubectl exec -n ainflue deployment/ainflue-api -- psql $DATABASE_URL -c "
CREATE INDEX CONCURRENTLY idx_uploads_created_at ON uploads(created_at);"

# 4. Enable caching
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: ainflue-config
  namespace: ainflue
data:
  REDIS_CACHE_ENABLED: "true"
  CACHE_TTL: "300"
EOF
```

### Infrastructure Issues

#### Node Resource Exhaustion
```bash
# Diagnosis
echo "=== DIAGNOSING NODE RESOURCE ISSUES ==="

# Check node resource usage
kubectl top nodes --sort-by=cpu
kubectl top nodes --sort-by=memory

# Check pod distribution across nodes
kubectl get pods -n ainflue -o wide | awk '{print $7}' | sort | uniq -c

# Check node conditions
kubectl describe nodes | grep -A 5 "Conditions:"

# Check disk usage on nodes
kubectl get nodes -o json | jq '.items[] | {name: .metadata.name, disk: .status.allocatable.storage}'

# Solutions:
# 1. Add more nodes to cluster
eksctl create nodegroup --cluster=ainflue-prod --name=emergency-nodes --instance-types=t3.large --nodes=3

# 2. Clean up unused images and containers
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: cleanup-nodes
spec:
  template:
    spec:
      hostPID: true
      hostNetwork: true
      containers:
      - name: cleanup
        image: busybox
        command: ["/bin/sh", "-c"]
        args:
        - |
          nsenter -t 1 -m -u -i -n docker system prune -af
          nsenter -t 1 -m -u -i -n docker volume prune -f
        securityContext:
          privileged: true
      restartPolicy: Never
EOF

# 3. Evict pods from problematic nodes
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data --force

# 4. Cordon nodes to prevent new pods
kubectl cordon <node-name>
```

#### Storage Issues
```bash
# Diagnosis
echo "=== DIAGNOSING STORAGE ISSUES ==="

# Check PVC status
kubectl get pvc -n ainflue

# Check storage class availability
kubectl get storageclass

# Check volume usage
kubectl exec -n ainflue deployment/ainflue-api -- df -h

# Check for storage-related events
kubectl get events -n ainflue --sort-by='.lastTimestamp' | grep -i "storage\|volume\|mount"

# Solutions:
# 1. Expand PVC if possible
kubectl patch pvc data-volume -n ainflue -p '{"spec":{"resources":{"requests":{"storage":"200Gi"}}}}'

# 2. Clean up old files
kubectl exec -n ainflue deployment/ainflue-api -- find /var/log -name "*.log" -mtime +7 -delete

# 3. Move to object storage
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: ainflue-config
  namespace: ainflue
data:
  STORAGE_TYPE: "s3"
  S3_BUCKET: "ainflue-content-prod"
  S3_REGION: "us-east-1"
EOF

# 4. Create new volume if corrupted
kubectl delete pvc corrupted-volume -n ainflue
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: new-data-volume
  namespace: ainflue
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: gp3
EOF
```

---

## ⚙️ Kubernetes Troubleshooting

### Pod Issues

#### Pods in CrashLoopBackOff
```bash
# Diagnosis
echo "=== DIAGNOSING CRASHLOOPBACKOFF ==="

# Find pods in crash loop
kubectl get pods -n ainflue | grep CrashLoopBackOff

# Get detailed pod information
POD_NAME=$(kubectl get pods -n ainflue | grep CrashLoopBackOff | awk '{print $1}' | head -1)
kubectl describe pod $POD_NAME -n ainflue

# Check logs from previous container instance
kubectl logs $POD_NAME -n ainflue --previous

# Check container exit codes
kubectl get pod $POD_NAME -n ainflue -o jsonpath='{.status.containerStatuses[0].lastState.terminated.exitCode}'

# Common exit codes and solutions:
# Exit code 1: General application error
kubectl logs $POD_NAME -n ainflue --previous | tail -50

# Exit code 125: Docker daemon error
kubectl describe pod $POD_NAME -n ainflue | grep -A 10 "Events:"

# Exit code 126: Container command not executable
kubectl get pod $POD_NAME -n ainflue -o yaml | grep -A 5 "command:"

# Exit code 127: Container command not found
kubectl exec $POD_NAME -n ainflue -- which python3

# Solutions:
# 1. Fix application configuration
kubectl edit configmap ainflue-config -n ainflue

# 2. Update image tag if corrupted
kubectl set image deployment/ainflue-api api=ainflue/api:v1.2.3-hotfix -n ainflue

# 3. Increase resource limits
kubectl patch deployment ainflue-api -n ainflue -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","resources":{"limits":{"memory":"1Gi","cpu":"500m"}}}]}}}}'

# 4. Add liveness/readiness probe delays
kubectl patch deployment ainflue-api -n ainflue -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","livenessProbe":{"initialDelaySeconds":60}}]}}}}'
```

#### Pods Stuck in Pending State
```bash
# Diagnosis
echo "=== DIAGNOSING PENDING PODS ==="

# Find pending pods
kubectl get pods -n ainflue | grep Pending

# Check pod events for scheduling issues
POD_NAME=$(kubectl get pods -n ainflue | grep Pending | awk '{print $1}' | head -1)
kubectl describe pod $POD_NAME -n ainflue | grep -A 10 "Events:"

# Check node resources
kubectl describe nodes | grep -A 5 "Allocated resources:"

# Check pod resource requests
kubectl describe pod $POD_NAME -n ainflue | grep -A 5 "Requests:"

# Common issues and solutions:
# 1. Insufficient node resources
kubectl get nodes -o custom-columns=NAME:.metadata.name,CPU-REQ:.status.allocatable.cpu,MEM-REQ:.status.allocatable.memory

# 2. Node selector/affinity issues
kubectl get pod $POD_NAME -n ainflue -o yaml | grep -A 10 "nodeSelector\|affinity"

# 3. Taints and tolerations
kubectl describe nodes | grep Taints
kubectl get pod $POD_NAME -n ainflue -o yaml | grep -A 5 "tolerations"

# 4. Storage class issues
kubectl get pvc -n ainflue | grep Pending
kubectl describe pvc -n ainflue

# Solutions:
# 1. Add more nodes
eksctl create nodegroup --cluster=ainflue-prod --name=additional-nodes --instance-types=t3.large --nodes=2

# 2. Remove node selector if too restrictive
kubectl patch deployment ainflue-api -n ainflue --type=merge -p='{"spec":{"template":{"spec":{"nodeSelector":null}}}}'

# 3. Add toleration for tainted nodes
kubectl patch deployment ainflue-api -n ainflue -p='{"spec":{"template":{"spec":{"tolerations":[{"key":"node-type","value":"gpu","effect":"NoSchedule"}]}}}}'

# 4. Use different storage class
kubectl patch pvc data-volume -n ainflue -p '{"spec":{"storageClassName":"gp2"}}'
```

### Service and Networking Issues

#### Service Not Accessible
```bash
# Diagnosis
echo "=== DIAGNOSING SERVICE ACCESSIBILITY ==="

# Check service status
kubectl get svc -n ainflue ainflue-api-service

# Check service endpoints
kubectl get endpoints -n ainflue ainflue-api-service

# Check if pods are running and ready
kubectl get pods -n ainflue -l app=ainflue-api -o wide

# Test service connectivity from within cluster
kubectl run debug-pod --rm -i --restart=Never --image=busybox -- /bin/sh -c "
echo 'Testing service connectivity...'
wget -qO- http://ainflue-api-service.ainflue.svc.cluster.local/health
"

# Check ingress configuration
kubectl get ingress -n ainflue
kubectl describe ingress ainflue-ingress -n ainflue

# Solutions:
# 1. Fix service selector
kubectl get svc ainflue-api-service -n ainflue -o yaml | grep -A 5 "selector:"
kubectl get pods -n ainflue -l app=ainflue-api --show-labels

# 2. Update service if selector mismatch
kubectl patch svc ainflue-api-service -n ainflue -p '{"spec":{"selector":{"app":"ainflue-api"}}}'

# 3. Check port configuration
kubectl describe svc ainflue-api-service -n ainflue | grep -A 5 "Port:"

# 4. Restart ingress controller if needed
kubectl rollout restart deployment ingress-nginx-controller -n ingress-nginx
```

#### DNS Resolution Issues
```bash
# Diagnosis
echo "=== DIAGNOSING DNS ISSUES ==="

# Test DNS resolution from pod
kubectl exec -n ainflue deployment/ainflue-api -- nslookup kubernetes.default.svc.cluster.local

# Check CoreDNS status
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Check CoreDNS configuration
kubectl get configmap coredns -n kube-system -o yaml

# Test external DNS resolution
kubectl exec -n ainflue deployment/ainflue-api -- nslookup google.com

# Solutions:
# 1. Restart CoreDNS pods
kubectl delete pods -n kube-system -l k8s-app=kube-dns

# 2. Check network policies
kubectl get networkpolicies -n ainflue

# 3. Verify cluster DNS settings
kubectl get svc -n kube-system kube-dns

# 4. Update DNS configuration if needed
kubectl edit configmap coredns -n kube-system
```

---

## 🗄️ Database Issues

### PostgreSQL Troubleshooting

#### High Connection Count
```bash
# Diagnosis
echo "=== DIAGNOSING HIGH CONNECTION COUNT ==="

# Check current connections
kubectl exec -n ainflue deployment/ainflue-api -- psql $DATABASE_URL -c "
SELECT count(*) as total_connections, 
       state, 
       application_name 
FROM pg_stat_activity 
GROUP BY state, application_name 
ORDER BY total_connections DESC;"

# Check maximum connections
kubectl exec -n ainflue deployment/ainflue-api -- psql $DATABASE_URL -c "
SHOW max_connections;"

# Check connection pool settings
kubectl get configmap ainflue-config -n ainflue -o yaml | grep -i pool

# Solutions:
# 1. Increase max_connections (requires restart)
aws rds modify-db-instance \
  --db-instance-identifier ainflue-prod-postgres \
  --db-parameter-group-name ainflue-postgres-params \
  --apply-immediately

# 2. Implement connection pooling
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pgbouncer
  namespace: ainflue
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pgbouncer
  template:
    metadata:
      labels:
        app: pgbouncer
    spec:
      containers:
      - name: pgbouncer
        image: pgbouncer/pgbouncer:latest
        env:
        - name: DATABASES_HOST
          value: "ainflue-prod-postgres.region.rds.amazonaws.com"
        - name: DATABASES_PORT
          value: "5432"
        - name: POOL_MODE
          value: "transaction"
        - name: MAX_CLIENT_CONN
          value: "1000"
EOF

# 3. Kill idle connections
kubectl exec -n ainflue deployment/ainflue-api -- psql $DATABASE_URL -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND state_change < now() - interval '5 minutes';"

# 4. Optimize application connection usage
kubectl patch deployment ainflue-api -n ainflue -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","env":[{"name":"DB_POOL_SIZE","value":"10"}]}]}}}}'
```

#### Slow Query Performance
```bash
# Diagnosis
echo "=== DIAGNOSING SLOW QUERIES ==="

# Enable slow query logging (if not already enabled)
kubectl exec -n ainflue deployment/ainflue-api -- psql $DATABASE_URL -c "
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();"

# Check slow queries
kubectl exec -n ainflue deployment/ainflue-api -- psql $DATABASE_URL -c "
SELECT query, 
       mean_time, 
       calls, 
       total_time,
       rows,
       100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"

# Check for missing indices
kubectl exec -n ainflue deployment/ainflue-api -- psql $DATABASE_URL -c "
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats 
WHERE schemaname = 'public' 
AND n_distinct > 100;"

# Solutions:
# 1. Add missing indices
kubectl exec -n ainflue deployment/ainflue-api -- psql $DATABASE_URL -c "
CREATE INDEX CONCURRENTLY idx_uploads_creator_id_created_at 
ON uploads(creator_id, created_at);"

# 2. Update table statistics
kubectl exec -n ainflue deployment/ainflue-api -- psql $DATABASE_URL -c "
ANALYZE uploads;
ANALYZE creators;
ANALYZE subscriptions;"

# 3. Optimize expensive queries
kubectl exec -n ainflue deployment/ainflue-api -- psql $DATABASE_URL -c "
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM uploads 
WHERE creator_id = 123 
ORDER BY created_at DESC 
LIMIT 20;"

# 4. Increase database resources
aws rds modify-db-instance \
  --db-instance-identifier ainflue-prod-postgres \
  --db-instance-class db.r5.xlarge \
  --apply-immediately
```

### Redis Troubleshooting

#### High Memory Usage
```bash
# Diagnosis
echo "=== DIAGNOSING REDIS MEMORY USAGE ==="

# Check Redis memory usage
kubectl exec -n ainflue deployment/redis-master -- redis-cli INFO memory

# Check key distribution
kubectl exec -n ainflue deployment/redis-master -- redis-cli --bigkeys

# Check for memory leaks
kubectl exec -n ainflue deployment/redis-master -- redis-cli INFO stats | grep "evicted_keys\|expired_keys"

# Solutions:
# 1. Set memory limits and eviction policy
kubectl exec -n ainflue deployment/redis-master -- redis-cli CONFIG SET maxmemory 2gb
kubectl exec -n ainflue deployment/redis-master -- redis-cli CONFIG SET maxmemory-policy allkeys-lru

# 2. Clean up old keys
kubectl exec -n ainflue deployment/redis-master -- redis-cli EVAL "
for i=1,redis.call('SCAN',0,'MATCH','session:*','COUNT',1000)[2] do 
  if redis.call('TTL',i) == -1 then 
    redis.call('EXPIRE',i,3600) 
  end 
end" 0

# 3. Implement key expiration
kubectl patch configmap ainflue-config -n ainflue -p '{"data":{"REDIS_DEFAULT_TTL":"3600"}}'

# 4. Scale Redis cluster
kubectl scale statefulset redis --replicas=3 -n ainflue
```

---

## 🌐 Network and Connectivity

### Load Balancer Issues

#### 502/503 Bad Gateway Errors
```bash
# Diagnosis
echo "=== DIAGNOSING LOAD BALANCER ERRORS ==="

# Check load balancer health
kubectl get svc -n ingress-nginx ingress-nginx-controller

# Check backend pod health
kubectl get pods -n ainflue -l app=ainflue-api -o custom-columns=NAME:.metadata.name,READY:.status.containerStatuses[0].ready,STATUS:.status.phase

# Check ingress configuration
kubectl describe ingress ainflue-ingress -n ainflue

# Check load balancer logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller --tail=100 | grep -E "502|503|error"

# Solutions:
# 1. Fix unhealthy pods
kubectl get pods -n ainflue -l app=ainflue-api --field-selector=status.phase!=Running
kubectl delete pods -n ainflue -l app=ainflue-api --field-selector=status.phase!=Running

# 2. Check readiness probes
kubectl describe deployment ainflue-api -n ainflue | grep -A 5 "Readiness:"

# 3. Increase backend timeout
kubectl patch ingress ainflue-ingress -n ainflue -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/proxy-read-timeout":"60"}}}'

# 4. Restart ingress controller
kubectl rollout restart deployment ingress-nginx-controller -n ingress-nginx
```

#### SSL/TLS Certificate Issues
```bash
# Diagnosis
echo "=== DIAGNOSING SSL CERTIFICATE ISSUES ==="

# Check certificate status
kubectl describe certificate ainflue-tls -n ainflue

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager --tail=50

# Check certificate expiration
kubectl get certificate ainflue-tls -n ainflue -o jsonpath='{.status.notAfter}'

# Test SSL configuration
echo | openssl s_client -connect api.ainflue.com:443 -servername api.ainflue.com 2>/dev/null | openssl x509 -noout -dates

# Solutions:
# 1. Force certificate renewal
kubectl delete certificate ainflue-tls -n ainflue
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: ainflue-tls
  namespace: ainflue
spec:
  secretName: ainflue-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - api.ainflue.com
EOF

# 2. Check DNS configuration
dig api.ainflue.com A
dig _acme-challenge.api.ainflue.com TXT

# 3. Verify cluster issuer
kubectl describe clusterissuer letsencrypt-prod

# 4. Manual certificate creation (emergency)
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
  -subj "/CN=api.ainflue.com" \
  -keyout tls.key -out tls.crt
kubectl create secret tls ainflue-tls-manual \
  --cert=tls.crt --key=tls.key -n ainflue
```

### Network Policy Issues

#### Pod-to-Pod Communication Blocked
```bash
# Diagnosis
echo "=== DIAGNOSING NETWORK POLICY ISSUES ==="

# Check network policies
kubectl get networkpolicies -n ainflue

# Test connectivity between pods
kubectl run test-pod --rm -i --restart=Never --image=busybox -- /bin/sh -c "
echo 'Testing API connectivity...'
wget -qO- http://ainflue-api-service.ainflue.svc.cluster.local:80/health
"

# Check CNI plugin logs
kubectl logs -n kube-system daemonset/calico-node --tail=50

# Solutions:
# 1. Create allow-all network policy (temporary)
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-all-temporary
  namespace: ainflue
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - {}
  egress:
  - {}
EOF

# 2. Fix specific network policy
kubectl get networkpolicy restrictive-policy -n ainflue -o yaml

# 3. Allow specific communication
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-db
  namespace: ainflue
spec:
  podSelector:
    matchLabels:
      app: ainflue-api
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 5432
EOF

# 4. Debug with tcpdump
kubectl exec -n ainflue deployment/ainflue-api -- tcpdump -i eth0 -n port 5432
```

---

## ⚡ Performance Issues

### CPU and Memory Optimization

#### High CPU Usage
```bash
# Diagnosis
echo "=== DIAGNOSING HIGH CPU USAGE ==="

# Check pod CPU usage
kubectl top pods -n ainflue --sort-by=cpu

# Check CPU throttling
kubectl exec -n ainflue deployment/ainflue-api -- cat /sys/fs/cgroup/cpu/cpu.stat | grep throttled

# Check application metrics
kubectl port-forward -n ainflue deployment/ainflue-api 6060:6060 &
curl http://localhost:6060/debug/pprof/profile?seconds=30 > cpu.prof
go tool pprof cpu.prof

# Solutions:
# 1. Increase CPU limits
kubectl patch deployment ainflue-api -n ainflue -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","resources":{"limits":{"cpu":"2000m"}}}]}}}}'

# 2. Scale horizontally
kubectl scale deployment ainflue-api --replicas=5 -n ainflue

# 3. Optimize code (if application issue)
kubectl logs -n ainflue deployment/ainflue-api | grep -i "slow\|timeout\|performance"

# 4. Enable CPU auto-scaling
kubectl apply -f - <<EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ainflue-api-hpa
  namespace: ainflue
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ainflue-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
EOF
```

#### Memory Optimization
```bash
# Diagnosis
echo "=== DIAGNOSING MEMORY ISSUES ==="

# Check memory usage trends
kubectl top pods -n ainflue --sort-by=memory

# Check for memory leaks
kubectl exec -n ainflue deployment/ainflue-api -- ps aux --sort=-%mem | head -10

# Get memory profile
curl http://localhost:6060/debug/pprof/heap > heap.prof
go tool pprof heap.prof

# Solutions:
# 1. Increase memory limits
kubectl patch deployment ainflue-api -n ainflue -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","resources":{"limits":{"memory":"2Gi"}}}]}}}}'

# 2. Implement memory-aware auto-scaling
kubectl patch hpa ainflue-api-hpa -n ainflue -p '{"spec":{"metrics":[{"type":"Resource","resource":{"name":"memory","target":{"type":"Utilization","averageUtilization":80}}}]}}'

# 3. Add garbage collection tuning
kubectl patch deployment ainflue-api -n ainflue -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","env":[{"name":"GOGC","value":"100"}]}]}}}}'

# 4. Restart pods with high memory usage
kubectl get pods -n ainflue -l app=ainflue-api -o json | \
  jq -r '.items[] | select(.status.containerStatuses[0].restartCount > 3) | .metadata.name' | \
  xargs kubectl delete pod -n ainflue
```

---

## 🎨 Creator Economy Specific Issues

### Content Upload Issues

#### Upload Failures
```bash
# Diagnosis
echo "=== DIAGNOSING UPLOAD FAILURES ==="

# Check upload service status
kubectl get pods -n ainflue -l component=upload-service

# Check S3 connectivity
kubectl exec -n ainflue deployment/upload-service -- aws s3 ls s3://ainflue-content-prod/ --region us-east-1

# Check upload queue status
kubectl exec -n ainflue deployment/redis-master -- redis-cli LLEN upload_queue

# Check recent upload errors
kubectl logs -n ainflue -l component=upload-service --since=1h | grep -i "error\|failed"

# Solutions:
# 1. Clear failed uploads from queue
kubectl exec -n ainflue deployment/redis-master -- redis-cli DEL upload_queue_failed

# 2. Restart upload service
kubectl rollout restart deployment/upload-service -n ainflue

# 3. Check S3 permissions
aws iam get-role-policy --role-name AinflueUploadRole --policy-name S3UploadPolicy

# 4. Scale upload workers
kubectl scale deployment upload-workers --replicas=5 -n ainflue
```

#### AI Processing Delays
```bash
# Diagnosis
echo "=== DIAGNOSING AI PROCESSING DELAYS ==="

# Check AI processing queue
kubectl exec -n ainflue deployment/redis-master -- redis-cli LLEN ai_processing_queue

# Check GPU node availability
kubectl get nodes -l node-type=gpu -o wide

# Check AI processing pod status
kubectl get pods -n ainflue -l component=ai-processor

# Solutions:
# 1. Scale AI processing pods
kubectl scale deployment ai-processor --replicas=3 -n ainflue

# 2. Add GPU nodes if needed
eksctl create nodegroup --cluster=ainflue-prod \
  --name=gpu-nodes \
  --instance-types=p3.2xlarge \
  --nodes=2 \
  --nodes-min=0 \
  --nodes-max=5

# 3. Optimize AI model inference
kubectl patch deployment ai-processor -n ainflue -p '{"spec":{"template":{"spec":{"containers":[{"name":"processor","env":[{"name":"BATCH_SIZE","value":"8"}]}]}}}}'

# 4. Implement processing priority queue
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-processor-config
  namespace: ainflue
data:
  ENABLE_PRIORITY_QUEUE: "true"
  HIGH_PRIORITY_THRESHOLD: "premium_creator"
EOF
```

### Revenue Processing Issues

#### Payment Processing Delays
```bash
# Diagnosis
echo "=== DIAGNOSING PAYMENT PROCESSING ==="

# Check payment service status
kubectl get pods -n ainflue -l component=payment-service

# Check payment queue
kubectl exec -n ainflue deployment/redis-master -- redis-cli LLEN payment_queue

# Check Stripe connectivity
kubectl exec -n ainflue deployment/payment-service -- curl -I https://api.stripe.com/v1/charges

# Solutions:
# 1. Process stuck payments
kubectl exec -n ainflue deployment/payment-service -- python manage.py process_stuck_payments

# 2. Scale payment workers
kubectl scale deployment payment-workers --replicas=3 -n ainflue

# 3. Check webhook endpoints
kubectl logs -n ainflue -l component=payment-service | grep webhook

# 4. Retry failed payments
kubectl exec -n ainflue deployment/redis-master -- redis-cli LRANGE payment_queue_failed 0 -1
```

---

## 📞 Emergency Contacts

### Escalation Matrix
```yaml
Emergency_Contacts:
  P0_Critical_Issues:
    Primary: Fahed Mlaiel (CTO) - +49-xxx-xxx-xxxx
    Secondary: Infrastructure Team Lead - +49-xxx-xxx-xxxx
    Tertiary: External Support - support@vendor.com
  
  Database_Issues:
    Primary: Database Team - db-team@ainflue.com
    Secondary: AWS Support - Enterprise Support Case
  
  Security_Incidents:
    Primary: Security Team - security@ainflue.com
    Secondary: Legal Team - legal@ainflue.com
    External: Incident Response Partner
  
  Network_Issues:
    Primary: Network Team - network@ainflue.com
    Secondary: Cloud Provider Support
```

### External Resources
```yaml
External_Support:
  AWS_Support: Enterprise Support - Case Portal
  Google_Cloud: Premium Support - Support Console
  Kubernetes: Community Forums + CNCF Slack
  Monitoring: Vendor Support Channels
  
Documentation_Links:
  Internal_Runbooks: https://docs.ainflue.com/runbooks/
  Architecture_Docs: https://docs.ainflue.com/architecture/
  API_Documentation: https://api-docs.ainflue.com/
  Monitoring_Dashboards: https://grafana.ainflue.com/
```

---

**© 2025 Fahed Mlaiel. All rights reserved.**  
**Contact:** mlaiel@live.de  
**Legal Notice:** This troubleshooting guide contains proprietary infrastructure procedures and diagnostic techniques. Unauthorized access or distribution is strictly prohibited.