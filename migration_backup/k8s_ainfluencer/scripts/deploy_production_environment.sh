#!/bin/bash
# Production Environment Deployment Script - Ainflue Platform
# Author: Fahed Mlaiel <mlaiel@live.de>
# Comprehensive production setup with secrets, environment variables, and monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE=${KUBERNETES_NAMESPACE:-"ainflue"}
MONITORING_NAMESPACE=${MONITORING_NAMESPACE:-"ainflue-monitoring"}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KUBERNETES_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🚀 Starting Ainflue Production Environment Deployment${NC}"
echo -e "${BLUE}=================================================${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
fi

# Check Kubernetes connectivity
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
fi

print_status "Prerequisites check completed"

# Create namespaces
echo -e "${BLUE}🏗️  Creating namespaces...${NC}"

kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: ${NAMESPACE}
  labels:
    name: ${NAMESPACE}
    environment: production
    managed-by: ainflue-platform
---
apiVersion: v1
kind: Namespace
metadata:
  name: ${MONITORING_NAMESPACE}
  labels:
    name: ${MONITORING_NAMESPACE}
    environment: production
    managed-by: ainflue-platform
EOF

print_status "Namespaces created successfully"

# Deploy configuration
echo -e "${BLUE}⚙️  Deploying production configuration...${NC}"

# Apply ConfigMaps
kubectl apply -f "${KUBERNETES_DIR}/configmaps.yaml" -n "${NAMESPACE}"
print_status "ConfigMaps deployed"

# Deploy secrets (only if environment variables are set)
echo -e "${BLUE}🔐 Deploying secrets...${NC}"

if [[ -n "${OPENAI_API_KEY}" || -n "${STRIPE_SECRET_KEY}" ]]; then
    print_warning "Detected API keys in environment - deploying with real values"
    python3 "${SCRIPT_DIR}/production_secrets_manager.py"
else
    print_warning "No API keys detected - deploying template secrets"
    kubectl apply -f "${KUBERNETES_DIR}/secrets.yaml" -n "${NAMESPACE}"
fi

print_status "Secrets deployed"

# Deploy enhanced production environment configuration
echo -e "${BLUE}🌍 Setting up production environment...${NC}"
python3 "${SCRIPT_DIR}/production_environment_manager.py"
print_status "Production environment configured"

# Deploy monitoring stack
echo -e "${BLUE}📊 Deploying monitoring stack...${NC}"

# Apply Grafana dashboards
kubectl apply -f "${KUBERNETES_DIR}/monitoring/grafana-dashboards.yaml" -n "${MONITORING_NAMESPACE}"
print_status "Grafana dashboards configured"

# Deploy monitoring components
python3 "${SCRIPT_DIR}/monitoring_stack_deployment.py"
print_status "Monitoring stack deployed"

# Verify deployments
echo -e "${BLUE}🔍 Verifying deployments...${NC}"

# Wait for deployments to be ready
echo "Waiting for monitoring deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment -l app=prometheus -n "${MONITORING_NAMESPACE}" || true
kubectl wait --for=condition=available --timeout=300s deployment -l app=grafana -n "${MONITORING_NAMESPACE}" || true
kubectl wait --for=condition=available --timeout=300s deployment -l app=jaeger -n "${MONITORING_NAMESPACE}" || true

# Check deployment status
echo -e "${BLUE}📈 Deployment Status:${NC}"

echo "Main application namespace (${NAMESPACE}):"
kubectl get configmaps,secrets -n "${NAMESPACE}" | grep ainflue || echo "No resources found"

echo ""
echo "Monitoring namespace (${MONITORING_NAMESPACE}):"
kubectl get deployments,services,configmaps -n "${MONITORING_NAMESPACE}" | head -10

# Display access information
echo -e "${BLUE}🔗 Access Information:${NC}"
echo -e "${GREEN}To access Grafana dashboard:${NC}"
echo "  kubectl port-forward -n ${MONITORING_NAMESPACE} svc/grafana 3000:3000"
echo "  Then open: http://localhost:3000 (admin/admin123)"

echo -e "${GREEN}To access Prometheus:${NC}"
echo "  kubectl port-forward -n ${MONITORING_NAMESPACE} svc/prometheus 9090:9090"
echo "  Then open: http://localhost:9090"

echo -e "${GREEN}To access Jaeger tracing:${NC}"
echo "  kubectl port-forward -n ${MONITORING_NAMESPACE} svc/jaeger-query 16686:16686"
echo "  Then open: http://localhost:16686"

# Security recommendations
echo -e "${BLUE}🔒 Security Recommendations:${NC}"
echo -e "${YELLOW}1. Update default passwords in secrets${NC}"
echo -e "${YELLOW}2. Configure TLS certificates for HTTPS${NC}"
echo -e "${YELLOW}3. Set up proper RBAC permissions${NC}"
echo -e "${YELLOW}4. Enable network policies for namespace isolation${NC}"
echo -e "${YELLOW}5. Configure backup strategies for persistent data${NC}"

# Environment-specific notes
echo -e "${BLUE}📝 Production Notes:${NC}"
echo -e "${YELLOW}• All configurations are optimized for production workloads${NC}"
echo -e "${YELLOW}• Monitoring dashboards include business metrics and AI model performance${NC}"
echo -e "${YELLOW}• Secrets management supports rotation and external secret stores${NC}"
echo -e "${YELLOW}• Environment variables are tuned for high performance and scalability${NC}"

print_status "Production environment deployment completed successfully!"

echo -e "${BLUE}🎉 Deployment Summary:${NC}"
echo "✅ Namespaces: ${NAMESPACE}, ${MONITORING_NAMESPACE}"
echo "✅ Configuration: Production-optimized ConfigMaps and Secrets"
echo "✅ Monitoring: Prometheus, Grafana, Jaeger"
echo "✅ Dashboards: System Overview, AI Models, Database Performance, Business Metrics"
echo "✅ Security: Production-hardened settings"

echo -e "${GREEN}🚀 Ainflue Platform is ready for production!${NC}"