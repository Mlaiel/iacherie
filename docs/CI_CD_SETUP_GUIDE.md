# 🚀 CI/CD Pipeline Complete Setup Guide

This document provides a comprehensive guide to set up and configure the complete CI/CD pipeline for the Ainflue platform.

## 📋 Overview

The CI/CD pipeline has been designed to meet all the requirements for a production-ready, enterprise-grade deployment system with:

- ✅ **Complete GitHub Actions pipeline** for all environments
- ✅ **Automated testing** before each deployment
- ✅ **Blue-Green deployment** for zero-downtime
- ✅ **Automated rollback** on failure with health monitoring
- ✅ **Approval workflows** for production deployments
- ✅ **Comprehensive smoke tests** post-deployment
- ✅ **Multi-channel notifications** to teams
- ✅ **Secure secrets management** with HashiCorp Vault
- ✅ **Artifact signing** for supply chain security
- ✅ **Enhanced security scanning** with SLSA compliance

## 🏗️ Pipeline Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Development   │    │     Staging     │    │   Production    │
│   Environment   │    │   Environment   │    │   Environment   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Automated CI   │    │ Staging Deploy  │    │Manual Approval  │
│  • Code Quality │    │ • Blue-Green    │    │ • Risk Analysis │
│  • Tests        │    │ • Smoke Tests   │    │ • Security Check│
│  • Security     │    │ • Integration   │    │ • Team Review   │
│  • Build        │    │ • Performance   │    │ • Compliance    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Artifact Build  │    │   Promotion     │    │ Production      │
│ • Docker Images │    │ • Signed        │    │ • Blue-Green    │
│ • SBOM Generate │    │ • Verified      │    │ • Health Checks │
│ • Signing       │    │ • Documented    │    │ • Rollback      │
│ • Scanning      │    │ • Tested        │    │ • Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Setup Instructions

### 1. GitHub Repository Configuration

#### A. Create GitHub Environments

1. Go to your repository → Settings → Environments
2. Create three environments:

**Staging Environment:**
```yaml
Name: staging
Protection Rules:
  - No restrictions (auto-deploy on main branch)
Environment Secrets:
  - KUBE_CONFIG_STAGING
  - STAGING_DATABASE_URL
  - STAGING_API_KEY
```

**Production Approval Environment:**
```yaml
Name: production-approval
Protection Rules:
  - Required reviewers: [DevOps Team, Tech Leads]
  - Wait timer: 0 minutes
  - Branch protection: main branch only
Environment Secrets: (none required)
```

**Production Environment:**
```yaml
Name: production
Protection Rules:
  - Required reviewers: [DevOps Team, Security Team, Tech Leads]
  - Wait timer: 5 minutes
  - Branch protection: main branch and version tags only
Environment Secrets:
  - KUBE_CONFIG_PRODUCTION
  - PRODUCTION_DATABASE_URL
  - PRODUCTION_API_KEY
```

#### B. Configure Repository Secrets

Navigate to Settings → Secrets and variables → Actions and add:

**Container Registry & Signing:**
```
COSIGN_PRIVATE_KEY          # Cosign private key for artifact signing
COSIGN_PASSWORD             # Password for Cosign private key
GITHUB_TOKEN                # Automatically provided by GitHub
```

**Kubernetes Configuration:**
```
KUBE_CONFIG_STAGING         # Base64 encoded kubeconfig for staging
KUBE_CONFIG_PRODUCTION      # Base64 encoded kubeconfig for production
```

**HashiCorp Vault:**
```
VAULT_ADDR                  # Vault server address (e.g., https://vault.company.com)
VAULT_TOKEN                 # Vault authentication token
VAULT_NAMESPACE             # Vault namespace (if using Vault Enterprise)
```

**Database & Services:**
```
DATABASE_URL                # Production database URL
STAGING_DATABASE_URL        # Staging database URL
REDIS_URL                   # Redis connection URL
```

**API Keys & External Services:**
```
OPENAI_API_KEY             # OpenAI API key for AI features
STRIPE_SECRET_KEY          # Stripe secret key for payments
ADMIN_API_TOKEN            # Admin API token for management operations
```

**Monitoring & Observability:**
```
DATADOG_API_KEY            # Datadog API key for metrics
SENTRY_AUTH_TOKEN          # Sentry authentication token
SENTRY_ORG                 # Sentry organization name
```

**CDN & Infrastructure:**
```
CLOUDFLARE_API_TOKEN       # Cloudflare API token for CDN management
CLOUDFLARE_ZONE_ID         # Cloudflare zone ID
```

**Security Scanning:**
```
SNYK_TOKEN                 # Snyk API token for vulnerability scanning
FOSSA_API_KEY              # FOSSA API key for license compliance
SEMGREP_APP_TOKEN          # Semgrep token for static analysis
```

**Notifications:**
```
SLACK_WEBHOOK_URL          # Main Slack webhook for notifications
SLACK_WEBHOOK_DEPLOYMENTS  # Dedicated deployment notifications channel
SLACK_WEBHOOK_ALERTS       # Critical alerts channel
TEAMS_WEBHOOK_URL          # Microsoft Teams webhook
DISCORD_WEBHOOK_URL        # Discord webhook
EMAIL_API_KEY              # Email service API key (SendGrid, etc.)
EMAIL_RECIPIENTS           # Comma-separated list of email recipients
TWILIO_ACCOUNT_SID         # Twilio account SID for SMS
TWILIO_AUTH_TOKEN          # Twilio auth token
TWILIO_PHONE_NUMBERS       # Comma-separated list of phone numbers for SMS
```

### 2. HashiCorp Vault Setup

#### A. Install and Configure Vault

1. **Install Vault CLI:**
```bash
# On Ubuntu/Debian
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt update && sudo apt install vault

# On macOS
brew install vault
```

2. **Initialize Vault Secrets:**
```bash
# Set environment variables
export VAULT_ADDR="https://your-vault-server.com"
export VAULT_TOKEN="your-vault-token"

# Create secret paths for each environment
vault kv put secret/ainflue/production \
  postgres-password="$(openssl rand -base64 32)" \
  redis-password="$(openssl rand -base64 32)" \
  jwt-secret="$(openssl rand -base64 64)" \
  api-key="$(openssl rand -hex 32)" \
  encryption-key="$(openssl rand -base64 32)"

vault kv put secret/ainflue/staging \
  postgres-password="$(openssl rand -base64 32)" \
  redis-password="$(openssl rand -base64 32)" \
  jwt-secret="$(openssl rand -base64 64)" \
  api-key="$(openssl rand -hex 32)"
```

### 3. Kubernetes Configuration

#### A. Create Kubernetes Manifests

Create the following directory structure:
```
kubernetes/
├── environments/
│   ├── staging/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   └── production/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── ingress.yaml
└── secrets/
    └── production-secrets.yaml
```

#### B. Sample Deployment Configuration

**kubernetes/environments/production/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ainflue-api-green
  namespace: ainflue
  labels:
    app: ainflue
    version: green
    environment: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ainflue
      version: green
  template:
    metadata:
      labels:
        app: ainflue
        version: green
        environment: production
    spec:
      containers:
      - name: ainflue
        image: ghcr.io/mlaiel/ainflue:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ainflue-secrets
              key: postgres-password
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ainflue-secrets
              key: redis-password
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

### 4. Artifact Signing Setup

#### A. Generate Cosign Key Pair

```bash
# Install Cosign
curl -O -L "https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64"
sudo mv cosign-linux-amd64 /usr/local/bin/cosign
sudo chmod +x /usr/local/bin/cosign

# Generate key pair
cosign generate-key-pair

# This creates:
# - cosign.key (private key) → Add to COSIGN_PRIVATE_KEY secret
# - cosign.pub (public key) → Keep for verification
```

#### B. Add Keys to GitHub Secrets

```bash
# Add private key to GitHub secrets
# Copy the content of cosign.key to COSIGN_PRIVATE_KEY secret
cat cosign.key

# The password you used during generation goes to COSIGN_PASSWORD secret
```

### 5. Notification Channels Setup

#### A. Slack Configuration

1. Create Slack webhooks for different channels:
   - #production-deployments → SLACK_WEBHOOK_DEPLOYMENTS
   - #alerts → SLACK_WEBHOOK_ALERTS
   - #general → SLACK_WEBHOOK_URL

2. Configure webhook URLs in GitHub secrets

#### B. Microsoft Teams Configuration

1. Add an "Incoming Webhook" connector to your Teams channel
2. Copy webhook URL to TEAMS_WEBHOOK_URL secret

#### C. Discord Configuration

1. Go to Server Settings → Integrations → Webhooks
2. Create new webhook and copy URL to DISCORD_WEBHOOK_URL secret

### 6. Monitoring Integration

#### A. Datadog Setup

```bash
# Add Datadog API key to GitHub secrets
# Configure Datadog agent in Kubernetes cluster

# Example Datadog agent configuration
kubectl apply -f https://raw.githubusercontent.com/DataDog/datadog-agent/main/Dockerfiles/manifests/agent.yaml
```

#### B. Sentry Setup

1. Create new Sentry project
2. Generate auth token with project write permissions
3. Add SENTRY_AUTH_TOKEN and SENTRY_ORG to GitHub secrets

## 🔄 Workflow Triggers

### Automatic Triggers

- **Push to `main` branch:** Triggers staging deployment
- **Tag creation (`v*`):** Triggers production deployment pipeline
- **Pull requests:** Triggers CI validation and security scanning
- **Schedule:** Daily security scans at 2 AM UTC

### Manual Triggers

- **workflow_dispatch:** Manual deployment with environment selection
- **Emergency deployment:** Skip approval with `[EMERGENCY]` or `[HOTFIX]` in commit message

## 📊 Pipeline Stages

### 1. Continuous Integration (CI)
- Code quality checks (Black, Flake8, MyPy)
- Unit and integration tests
- Security scanning (SAST, dependency vulnerabilities)
- Container image building and scanning
- Artifact signing and SBOM generation

### 2. Staging Deployment
- Automated deployment to staging environment
- Comprehensive smoke tests
- Performance validation
- Security verification
- Integration testing

### 3. Production Approval
- Risk assessment based on changes
- Security score evaluation
- Manual approval requirement
- Team notifications (Slack, Teams, Email)
- Emergency bypass option

### 4. Production Deployment
- Blue-green deployment strategy
- Gradual traffic switching (10% → 50% → 100%)
- Health monitoring with exponential backoff
- Automatic rollback on failure
- Post-deployment verification

### 5. Post-Deployment
- Database migrations
- Cache warming
- CDN cache purging
- Monitoring system updates
- Success notifications

## 🔒 Security Features

### Supply Chain Security
- Container image signing with Cosign
- SLSA Level 2 compliance
- Software Bill of Materials (SBOM) generation
- Dependency vulnerability scanning
- License compliance checking

### Secrets Management
- HashiCorp Vault integration
- Automatic secret rotation
- Kubernetes secret synchronization
- Audit logging and compliance

### Access Control
- GitHub environment protection rules
- Required approvers for production
- Branch protection policies
- Secure artifact registry access

## 📈 Monitoring & Observability

### Deployment Metrics
- Deployment frequency
- Lead time for changes
- Mean time to recovery (MTTR)
- Change failure rate

### Health Monitoring
- Application health checks
- Performance metrics
- Error rate monitoring
- Security alert tracking

### Notification Channels
- Real-time Slack notifications
- Email alerts for critical events
- SMS notifications for emergencies
- Microsoft Teams integration

## 🚨 Troubleshooting

### Common Issues

1. **Deployment Approval Timeout:**
   - Check GitHub environment protection rules
   - Verify required reviewers are available
   - Review approval workflow logs

2. **Vault Secret Access:**
   - Verify VAULT_TOKEN permissions
   - Check secret path configuration
   - Confirm Vault server connectivity

3. **Container Signing Failures:**
   - Verify Cosign key configuration
   - Check COSIGN_PRIVATE_KEY format
   - Confirm COSIGN_PASSWORD accuracy

4. **Health Check Failures:**
   - Review application logs
   - Check Kubernetes service configuration
   - Verify ingress controller setup

### Debugging Commands

```bash
# Check workflow status
gh run list --workflow="production-deployment.yml"

# View specific run logs
gh run view <run-id> --log

# Check Kubernetes deployment status
kubectl get deployments -n ainflue
kubectl describe deployment ainflue-api-green -n ainflue

# Verify secrets
kubectl get secrets -n ainflue
kubectl describe secret ainflue-secrets -n ainflue

# Check Vault connectivity
vault status
vault kv get secret/ainflue/production
```

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [Cosign Documentation](https://docs.sigstore.dev/cosign/overview/)
- [SLSA Framework](https://slsa.dev/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

## 🔄 Maintenance

### Regular Tasks

1. **Weekly:**
   - Review security scan results
   - Check secret rotation schedules
   - Verify backup procedures

2. **Monthly:**
   - Update base container images
   - Rotate Vault tokens
   - Review access permissions

3. **Quarterly:**
   - Security audit of pipeline
   - Performance optimization review
   - Disaster recovery testing

---

**Last Updated:** December 2024  
**Version:** 1.0  
**Author:** Fahed Mlaiel (mlaiel@live.de)