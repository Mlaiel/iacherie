# 🔧 Ainflue Infrastructure Troubleshooting Guide

**Enterprise Troubleshooting Procedures and Solutions**

## 📋 Overview

This guide provides comprehensive troubleshooting procedures for the Ainflue Infrastructure module, covering common issues, diagnostic procedures, and resolution steps.

## 🎯 Troubleshooting Methodology

### Diagnostic Approach
1. **Identify Symptoms** - Gather error messages and symptoms
2. **Isolate Components** - Determine affected infrastructure components
3. **Analyze Logs** - Review relevant logs and metrics
4. **Test Hypotheses** - Systematically test potential causes
5. **Implement Solutions** - Apply appropriate fixes
6. **Verify Resolution** - Confirm issue is resolved
7. **Document Findings** - Update knowledge base

### Escalation Levels
- **Level 1**: Basic troubleshooting and known issues
- **Level 2**: Complex issues requiring infrastructure expertise
- **Level 3**: Critical issues requiring architectural changes
- **Emergency**: Service-affecting issues requiring immediate response

## 🚨 Common Infrastructure Issues

### 1. Resource Provisioning Failures

#### Symptoms
- Resources fail to deploy
- Timeout errors during provisioning
- Authentication errors with cloud providers
- Resource quota exceeded errors

#### Diagnostic Commands
```bash
# Check resource status
kubectl get pods -n ainflue-system
kubectl describe pod <pod-name> -n ainflue-system

# Check cloud provider quotas
aws service-quotas list-service-quotas --service-code ec2
gcloud compute project-info describe --project=<project-id>
az vm list-usage --location eastus

# Check authentication
aws sts get-caller-identity
gcloud auth list
az account show
```

#### Common Causes and Solutions

**Authentication Issues**
```bash
# AWS credentials
aws configure list
export AWS_ACCESS_KEY_ID=<key>
export AWS_SECRET_ACCESS_KEY=<secret>

# GCP service account
gcloud auth activate-service-account --key-file=<path-to-key>
export GOOGLE_APPLICATION_CREDENTIALS=<path-to-key>

# Azure authentication
az login --service-principal -u <app-id> -p <password> --tenant <tenant>
```

**Resource Quota Issues**
```bash
# Request quota increase
aws service-quotas request-service-quota-increase \
  --service-code ec2 \
  --quota-code L-1216C47A \
  --desired-value 100

# Check GCP quotas
gcloud compute project-info describe --project=<project-id> \
  --format="table(quotas.metric,quotas.usage,quotas.limit)"
```

**Network Connectivity Issues**
```bash
# Test connectivity
curl -v https://aws.amazon.com
curl -v https://cloud.google.com
curl -v https://azure.microsoft.com

# Check DNS resolution
nslookup ec2.amazonaws.com
nslookup compute.googleapis.com
nslookup management.azure.com
```

### 2. Container Orchestration Issues

#### Pod Startup Problems

**ImagePullBackOff Errors**
```bash
# Check image repository access
docker pull <image-name>

# Check imagePullSecrets
kubectl get secrets -n ainflue-system
kubectl describe secret <registry-secret> -n ainflue-system

# Update image pull secret
kubectl create secret docker-registry <secret-name> \
  --docker-server=<registry-url> \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email>
```

**Resource Constraints**
```bash
# Check node resources
kubectl top nodes
kubectl describe node <node-name>

# Check pod resource requests/limits
kubectl describe pod <pod-name> -n ainflue-system

# Scale cluster if needed
eksctl scale nodegroup --cluster=<cluster-name> \
  --nodes=5 --nodes-min=3 --nodes-max=10 <nodegroup-name>
```

**Persistent Volume Issues**
```bash
# Check PV/PVC status
kubectl get pv
kubectl get pvc -n ainflue-system
kubectl describe pvc <pvc-name> -n ainflue-system

# Check storage class
kubectl get storageclass
kubectl describe storageclass <storage-class-name>

# Manually create PV if needed
kubectl apply -f persistent-volume.yaml
```

### 3. Network Connectivity Issues

#### Service Discovery Problems

**DNS Resolution Issues**
```bash
# Test DNS from within cluster
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default

# Check CoreDNS logs
kubectl logs -n kube-system -l k8s-app=kube-dns

# Restart CoreDNS
kubectl rollout restart deployment/coredns -n kube-system
```

**Service Mesh Issues (Istio)**
```bash
# Check Istio components
kubectl get pods -n istio-system
istioctl proxy-status

# Check sidecar injection
kubectl get namespace -L istio-injection
kubectl describe pod <pod-name> -n ainflue-system

# Debug proxy configuration
istioctl proxy-config cluster <pod-name> -n ainflue-system
```

**Load Balancer Issues**
```bash
# Check service status
kubectl get svc -n ainflue-system
kubectl describe svc <service-name> -n ainflue-system

# Check endpoints
kubectl get endpoints -n ainflue-system

# Test service connectivity
kubectl port-forward svc/<service-name> 8080:80 -n ainflue-system
```

### 4. Database Connectivity Issues

#### Connection Pool Exhaustion
```bash
# Check database connections
kubectl exec -it <postgres-pod> -n database -- \
  psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Check connection pool configuration
kubectl get configmap database-config -n database -o yaml

# Restart connection pool
kubectl rollout restart deployment/pgbouncer -n database
```

#### Database Performance Issues
```bash
# Check slow queries
kubectl exec -it <postgres-pod> -n database -- \
  psql -U postgres -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Check database metrics
kubectl port-forward svc/postgres-exporter 9187:9187 -n database
curl http://localhost:9187/metrics | grep postgres_
```

### 5. Performance Issues

#### High CPU/Memory Usage
```bash
# Check resource utilization
kubectl top pods -n ainflue-system
kubectl top nodes

# Check resource limits
kubectl describe pod <pod-name> -n ainflue-system | grep -A 5 "Limits\|Requests"

# Scale deployment if needed
kubectl scale deployment <deployment-name> --replicas=5 -n ainflue-system
```

#### Slow Response Times
```bash
# Check application metrics
curl http://infrastructure-orchestrator:8080/metrics | grep http_request_duration

# Check database performance
kubectl exec -it <postgres-pod> -n database -- \
  psql -U postgres -c "SELECT schemaname,tablename,attname,n_distinct,correlation FROM pg_stats;"

# Check network latency
kubectl exec -it <pod-name> -n ainflue-system -- ping <target-service>
```

### 6. Storage Issues

#### Disk Space Problems
```bash
# Check disk usage
kubectl exec -it <pod-name> -n ainflue-system -- df -h

# Check persistent volume usage
kubectl describe pv | grep -A 5 "Capacity\|Used"

# Clean up old logs
kubectl exec -it <pod-name> -n ainflue-system -- \
  find /var/log -name "*.log" -mtime +7 -delete
```

#### Backup Failures
```bash
# Check backup jobs
kubectl get jobs -n backup-system
kubectl describe job <backup-job> -n backup-system

# Check backup storage
aws s3 ls s3://ainflue-backups/
gsutil ls gs://ainflue-backups/

# Test backup restoration
kubectl apply -f test-restore-job.yaml
```

## 🔍 Monitoring and Alerting Issues

### 1. Prometheus Issues

#### Metrics Not Collected
```bash
# Check Prometheus targets
curl http://prometheus:9090/api/v1/targets | jq .

# Check service monitor
kubectl get servicemonitor -n monitoring
kubectl describe servicemonitor <monitor-name> -n monitoring

# Check metrics endpoint
curl http://<service>:<port>/metrics
```

#### Storage Issues
```bash
# Check Prometheus storage
kubectl exec -it prometheus-0 -n monitoring -- df -h /prometheus

# Check retention settings
kubectl get prometheus -n monitoring -o yaml | grep retention

# Compact Prometheus data
kubectl exec -it prometheus-0 -n monitoring -- \
  promtool tsdb create-blocks-from --help
```

### 2. Grafana Issues

#### Dashboard Loading Problems
```bash
# Check Grafana logs
kubectl logs deployment/grafana -n monitoring

# Check datasource connectivity
curl -u admin:password http://grafana:3000/api/datasources

# Reset admin password
kubectl exec -it deployment/grafana -n monitoring -- \
  grafana-cli admin reset-admin-password newpassword
```

### 3. Alerting Issues

#### Alerts Not Firing
```bash
# Check alerting rules
curl http://prometheus:9090/api/v1/rules | jq .

# Check Alertmanager status
curl http://alertmanager:9093/api/v1/status

# Test alert webhook
curl -X POST http://alertmanager:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{"labels":{"alertname":"test","severity":"warning"}}]'
```

## 🔒 Security Issues

### 1. Authentication Problems

#### Token Expiration
```bash
# Check token expiration
kubectl auth whoami
kubectl auth can-i create pods --as=system:serviceaccount:default:default

# Refresh tokens
kubectl config view --raw | grep token
gcloud auth print-access-token
az account get-access-token
```

#### RBAC Issues
```bash
# Check user permissions
kubectl auth can-i create deployments --as=<username>
kubectl describe clusterrolebinding | grep <username>

# Create service account and binding
kubectl create serviceaccount <account-name> -n <namespace>
kubectl create clusterrolebinding <binding-name> \
  --clusterrole=cluster-admin \
  --serviceaccount=<namespace>:<account-name>
```

### 2. Network Security Issues

#### Certificate Problems
```bash
# Check certificate expiration
kubectl get certificates -A
kubectl describe certificate <cert-name> -n <namespace>

# Renew certificates
kubectl delete certificate <cert-name> -n <namespace>
kubectl apply -f certificate.yaml

# Check TLS configuration
openssl s_client -connect <service>:443 -servername <hostname>
```

#### Network Policy Issues
```bash
# Check network policies
kubectl get networkpolicy -A
kubectl describe networkpolicy <policy-name> -n <namespace>

# Test network connectivity
kubectl exec -it <pod-name> -n <namespace> -- \
  nc -zv <target-service> <port>
```

## 💰 Cost Optimization Issues

### 1. Unexpected Cost Increases

#### Identify Cost Drivers
```bash
# Check resource utilization
kubectl top pods --all-namespaces --sort-by=cpu
kubectl top pods --all-namespaces --sort-by=memory

# Check persistent volumes
kubectl get pv --sort-by=.spec.capacity.storage

# Review cloud billing
aws ce get-cost-and-usage --time-period Start=2023-01-01,End=2023-01-31 \
  --granularity MONTHLY --metrics BlendedCost

gcloud billing accounts list
gcloud billing projects list --billing-account=<account-id>
```

#### Right-size Resources
```bash
# Analyze resource requests vs actual usage
kubectl describe pod <pod-name> | grep -A 10 "Requests\|Limits"
kubectl top pod <pod-name>

# Update resource requests
kubectl patch deployment <deployment-name> -p \
  '{"spec":{"template":{"spec":{"containers":[{"name":"<container>","resources":{"requests":{"cpu":"100m","memory":"128Mi"}}}]}}}}'
```

## 🔄 Disaster Recovery Issues

### 1. Backup Failures

#### Diagnose Backup Issues
```bash
# Check backup jobs
kubectl get jobs -n backup-system
kubectl logs job/<backup-job> -n backup-system

# Verify backup storage
aws s3 ls s3://ainflue-backups/ --recursive
gsutil ls gs://ainflue-backups/ -l

# Test backup integrity
kubectl apply -f backup-verification-job.yaml
```

### 2. Recovery Problems

#### Database Recovery Issues
```bash
# Check database status
kubectl get postgresql -n database
kubectl describe postgresql <postgres-cluster> -n database

# Restore from backup
kubectl apply -f postgres-restore.yaml

# Verify data integrity
kubectl exec -it <postgres-pod> -n database -- \
  psql -U postgres -c "SELECT count(*) FROM <table>;"
```

## 🛠️ Troubleshooting Tools

### 1. Diagnostic Scripts

#### Health Check Script
```bash
#!/bin/bash
# infrastructure-health-check.sh

echo "=== Infrastructure Health Check ==="

# Check cluster health
echo "Cluster Nodes:"
kubectl get nodes

echo "System Pods:"
kubectl get pods -n kube-system | grep -v Running

echo "Infrastructure Pods:"
kubectl get pods -n ainflue-system | grep -v Running

# Check critical services
echo "Critical Services:"
kubectl get svc -n ainflue-system

# Check resource usage
echo "Resource Usage:"
kubectl top nodes
kubectl top pods -n ainflue-system

echo "=== Health Check Complete ==="
```

#### Log Collection Script
```bash
#!/bin/bash
# collect-logs.sh

LOG_DIR="/tmp/ainflue-logs-$(date +%Y%m%d-%H%M%S)"
mkdir -p $LOG_DIR

echo "Collecting infrastructure logs..."

# Collect pod logs
for pod in $(kubectl get pods -n ainflue-system -o name); do
    pod_name=$(echo $pod | cut -d'/' -f2)
    kubectl logs $pod -n ainflue-system > $LOG_DIR/$pod_name.log
done

# Collect events
kubectl get events -n ainflue-system --sort-by='.lastTimestamp' > $LOG_DIR/events.log

# Collect resource descriptions
kubectl describe pods -n ainflue-system > $LOG_DIR/pod-descriptions.log

echo "Logs collected in: $LOG_DIR"
```

### 2. Performance Analysis Tools

#### Resource Monitor
```python
#!/usr/bin/env python3
# resource-monitor.py

import subprocess
import time
import json
from datetime import datetime

def get_resource_usage():
    """Get current resource usage."""
    try:
        # Get node metrics
        result = subprocess.run(['kubectl', 'top', 'nodes', '--no-headers'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    node_name = parts[0]
                    cpu_usage = parts[1]
                    cpu_percent = parts[2]
                    memory_usage = parts[3] 
                    memory_percent = parts[4]
                    
                    print(f"Node: {node_name}")
                    print(f"  CPU: {cpu_usage} ({cpu_percent})")
                    print(f"  Memory: {memory_usage} ({memory_percent})")
                    print()
    except Exception as e:
        print(f"Error getting resource usage: {e}")

def monitor_resources(interval=60):
    """Monitor resources continuously."""
    print("Starting resource monitoring...")
    while True:
        print(f"\n=== Resource Report - {datetime.now()} ===")
        get_resource_usage()
        time.sleep(interval)

if __name__ == "__main__":
    monitor_resources()
```

### 3. Network Diagnostic Tools

#### Connectivity Tester
```bash
#!/bin/bash
# connectivity-test.sh

echo "=== Network Connectivity Test ==="

# Test internal service connectivity
services=(
    "infrastructure-orchestrator:8080"
    "multi-cloud-manager:8080"
    "cost-manager:8080"
    "prometheus:9090"
    "grafana:3000"
)

for service in "${services[@]}"; do
    echo "Testing connectivity to $service..."
    if kubectl exec -it deployment/test-pod -- nc -zv $service 2>/dev/null; then
        echo "✓ $service is reachable"
    else
        echo "✗ $service is not reachable"
    fi
done

# Test external connectivity
external_services=(
    "aws.amazon.com:443"
    "cloud.google.com:443"
    "management.azure.com:443"
)

for service in "${external_services[@]}"; do
    echo "Testing external connectivity to $service..."
    if kubectl exec -it deployment/test-pod -- nc -zv $service 2>/dev/null; then
        echo "✓ $service is reachable"
    else
        echo "✗ $service is not reachable"
    fi
done

echo "=== Connectivity Test Complete ==="
```

## 📚 Knowledge Base

### Common Error Messages

#### "ImagePullBackOff"
- **Cause**: Cannot pull container image
- **Solution**: Check image name, registry credentials, network connectivity
- **Command**: `kubectl describe pod <pod> | grep -A 10 Events`

#### "CrashLoopBackOff"
- **Cause**: Pod keeps crashing after startup
- **Solution**: Check application logs, resource limits, health checks
- **Command**: `kubectl logs <pod> --previous`

#### "Pending"
- **Cause**: Pod cannot be scheduled
- **Solution**: Check node resources, taints/tolerations, resource requests
- **Command**: `kubectl describe pod <pod> | grep -A 10 Events`

#### "OutOfMemory"
- **Cause**: Container exceeded memory limit
- **Solution**: Increase memory limit or optimize application
- **Command**: `kubectl top pod <pod> --containers`

### Best Practices

#### Preventive Measures
1. **Regular Health Checks**: Implement automated health monitoring
2. **Resource Monitoring**: Track resource usage trends
3. **Capacity Planning**: Plan for growth and peak loads
4. **Backup Testing**: Regularly test backup and recovery procedures
5. **Security Scanning**: Continuous security vulnerability scanning
6. **Documentation**: Keep troubleshooting procedures updated

#### Emergency Response
1. **Incident Triage**: Quickly assess impact and severity
2. **Communication**: Notify stakeholders and team members
3. **Mitigation**: Implement immediate mitigation steps
4. **Investigation**: Conduct thorough root cause analysis
5. **Resolution**: Apply permanent fixes
6. **Post-Mortem**: Document lessons learned

### Escalation Contacts

#### Internal Teams
- **Infrastructure Team**: infrastructure@ainflue.com
- **Security Team**: security@ainflue.com
- **Database Team**: database@ainflue.com
- **Network Team**: network@ainflue.com

#### External Vendors
- **AWS Support**: Enterprise Support Case
- **Google Cloud Support**: Premium Support Case
- **Azure Support**: Professional Direct Case
- **Kubernetes Support**: CNCF Support Channels

### Emergency Procedures

#### Service Outage Response
1. **Immediate Assessment**: Determine scope and impact
2. **Incident Declaration**: Declare incident severity level
3. **Team Assembly**: Assemble response team
4. **Communication**: Update status page and stakeholders
5. **Mitigation**: Implement emergency mitigation
6. **Recovery**: Execute recovery procedures
7. **Validation**: Verify service restoration
8. **Post-Incident**: Conduct post-mortem analysis

#### Data Loss Response
1. **Stop Operations**: Prevent further data loss
2. **Assess Damage**: Determine scope of data loss
3. **Activate DR**: Execute disaster recovery plan
4. **Restore Data**: Restore from backups
5. **Verify Integrity**: Validate restored data
6. **Resume Operations**: Gradually restore services
7. **Investigate**: Determine root cause
8. **Improve**: Update procedures and safeguards

---

**Created by**: Fahed Mlaiel (mlaiel@live.de)  
**Version**: 1.0  
**Last Updated**: 2025  
**Classification**: Enterprise Troubleshooting Documentation

© 2025 Fahed Mlaiel. All rights reserved.