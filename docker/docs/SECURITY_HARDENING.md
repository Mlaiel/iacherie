# Docker Security Hardening Guide

## Enterprise Security for Ainflue Platform

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Version:** 3.0  
**Date:** September 2025

### Security Overview

This guide covers comprehensive security hardening for the Ainflue Docker infrastructure, ensuring enterprise-grade protection across all 80+ containerized services.

### Container Security

#### 1. Base Image Security
```dockerfile
# Use minimal, security-focused base images
FROM alpine:3.18 AS base
# or
FROM gcr.io/distroless/python3-debian11

# Update packages and remove package manager
RUN apk update && apk upgrade && \
    apk add --no-cache python3 py3-pip && \
    rm -rf /var/cache/apk/*
```

#### 2. Non-Root User Configuration
```dockerfile
# Create dedicated user for each service
RUN addgroup -g 10001 -S appgroup && \
    adduser -u 10001 -S appuser -G appgroup
USER appuser
```

#### 3. File System Security
```dockerfile
# Read-only root filesystem
FROM alpine:3.18
COPY app /app
RUN chmod -R 755 /app
USER 10001
```

### Image Security Scanning

#### 1. Trivy Integration
```bash
# Scan images for vulnerabilities
trivy image --severity HIGH,CRITICAL ainflue/audio-processor:latest

# Automated scanning in CI/CD
#!/bin/bash
docker build -t temp-image .
trivy image --exit-code 1 --severity HIGH,CRITICAL temp-image
if [ $? -eq 0 ]; then
    docker tag temp-image production-image:latest
fi
```

#### 2. Clair Scanner
```yaml
# docker-compose.security.yml
version: '3.8'
services:
  clair:
    image: quay.io/coreos/clair:latest
    environment:
      CLAIR_CONF: /config/config.yaml
    volumes:
      - ./clair-config:/config
```

### Network Security

#### 1. Network Segmentation
```yaml
# Isolated networks for different tiers
networks:
  frontend:
    driver: overlay
    attachable: true
  backend:
    driver: overlay
    internal: true
  database:
    driver: overlay
    internal: true
```

#### 2. Service Mesh Security (Istio)
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
spec:
  mtls:
    mode: STRICT
```

#### 3. Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: audio-policy
spec:
  podSelector:
    matchLabels:
      app: audio-processor
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 8000
```

### Secret Management

#### 1. Docker Secrets
```bash
# Create secrets
echo "supersecret" | docker secret create db_password -
echo "jwt-secret-key" | docker secret create jwt_secret -

# Use in compose file
version: '3.8'
services:
  api:
    secrets:
      - db_password
      - jwt_secret
secrets:
  db_password:
    external: true
  jwt_secret:
    external: true
```

#### 2. HashiCorp Vault Integration
```python
import hvac

client = hvac.Client(url='https://vault.ainflue.com:8200')
client.token = os.environ['VAULT_TOKEN']

# Read secret
secret = client.secrets.kv.v2.read_secret_version(path='database/credentials')
db_password = secret['data']['data']['password']
```

#### 3. Environment Variable Security
```dockerfile
# Avoid hardcoded secrets
ENV DATABASE_URL="postgresql://user:${DB_PASSWORD}@db:5432/ainflue"

# Use secret mounting instead
COPY --from=secrets /run/secrets/db_password /etc/secrets/
```

### Access Control

#### 1. RBAC Configuration
```yaml
# Kubernetes RBAC
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: audio-processor-role
rules:
- apiGroups: [""]
  resources: ["pods", "configmaps"]
  verbs: ["get", "list"]
```

#### 2. Service Authentication
```python
# JWT-based service authentication
import jwt
import datetime

def generate_service_token(service_name):
    payload = {
        'service': service_name,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
```

### Runtime Security

#### 1. Security Contexts
```yaml
services:
  audio-processor:
    security_opt:
      - no-new-privileges:true
      - apparmor:docker-default
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
```

#### 2. Resource Limits
```yaml
services:
  service-name:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
          pids: 100
        reservations:
          cpus: '0.5'
          memory: 512M
    ulimits:
      nofile: 65536
      nproc: 4096
```

### Monitoring and Audit

#### 1. Security Event Monitoring
```yaml
# Falco rules for container security
- rule: Shell in container
  desc: Notice shell activity within a container
  condition: spawned_process and shell_procs
  output: Shell spawned in container (user=%user.name container=%container.name)
  priority: WARNING
```

#### 2. Audit Logging
```json
{
  "audit": {
    "enabled": true,
    "log_format": "json",
    "log_path": "/var/log/docker-audit.log",
    "events": [
      "container_create",
      "container_start",
      "container_stop",
      "image_pull",
      "network_create"
    ]
  }
}
```

### Compliance

#### 1. CIS Docker Benchmark
```bash
# Run Docker Bench Security
git clone https://github.com/docker/docker-bench-security.git
cd docker-bench-security
./docker-bench-security.sh
```

#### 2. GDPR Compliance
```python
# Data encryption and anonymization
from cryptography.fernet import Fernet

class GDPRCompliantStorage:
    def __init__(self):
        self.cipher = Fernet(os.environ['ENCRYPTION_KEY'])
    
    def store_user_data(self, user_data):
        encrypted_data = self.cipher.encrypt(user_data.encode())
        # Store with expiration timestamp
        return encrypted_data
    
    def anonymize_data(self, user_id):
        # Remove PII while keeping analytics data
        pass
```

### Incident Response

#### 1. Security Incident Detection
```python
# Automated threat detection
def detect_anomalies():
    metrics = get_security_metrics()
    if metrics['failed_logins'] > THRESHOLD:
        trigger_security_alert('Multiple failed login attempts')
    
    if metrics['unusual_network_traffic']:
        isolate_container(suspicious_container_id)
```

#### 2. Container Isolation
```bash
# Emergency container isolation
docker network disconnect ainflue-network suspicious-container
docker update --cpus="0.1" --memory="100m" suspicious-container
```

### Security Automation

#### 1. Automated Patching
```yaml
# Watchtower for automatic updates
services:
  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      WATCHTOWER_SCHEDULE: "0 0 2 * * *"  # Daily at 2 AM
      WATCHTOWER_CLEANUP: true
```

#### 2. Security Scanning Pipeline
```yaml
# CI/CD security pipeline
name: Security Scan
on: [push, pull_request]
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build image
        run: docker build -t test-image .
      - name: Run Trivy scan
        run: trivy image --exit-code 1 test-image
      - name: Run Hadolint
        run: hadolint Dockerfile
```

### Best Practices

1. **Principle of Least Privilege**: Grant minimal necessary permissions
2. **Defense in Depth**: Implement multiple security layers
3. **Regular Updates**: Keep base images and dependencies updated
4. **Monitoring**: Implement comprehensive security monitoring
5. **Incident Response**: Have automated incident response procedures
6. **Compliance**: Regular compliance audits and remediation
7. **Training**: Security awareness training for development teams