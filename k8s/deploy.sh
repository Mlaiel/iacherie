#!/bin/bash

# Ainflue Platform Deployment Script
# Complete deployment automation for Kubernetes infrastructure
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="ainflue"
MONITORING_NAMESPACE="monitoring"
KUBECTL_TIMEOUT="300s"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed or not in PATH"
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster"
    fi
    
    # Check if running as correct user
    CURRENT_CONTEXT=$(kubectl config current-context)
    log "Current kubectl context: $CURRENT_CONTEXT"
    
    # Verify cluster has required resources
    if ! kubectl get nodes &> /dev/null; then
        error "Cannot access cluster nodes"
    fi
    
    log "Prerequisites check passed ✓"
}

# Create namespaces
create_namespaces() {
    log "Creating namespaces..."
    
    # Apply namespace configuration
    kubectl apply -f k8s/namespace.yaml --timeout=$KUBECTL_TIMEOUT
    
    # Create monitoring namespace if it doesn't exist
    kubectl create namespace $MONITORING_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # Wait for namespaces to be ready
    kubectl wait --for=condition=Active namespace/$NAMESPACE --timeout=$KUBECTL_TIMEOUT
    kubectl wait --for=condition=Active namespace/$MONITORING_NAMESPACE --timeout=$KUBECTL_TIMEOUT
    
    log "Namespaces created successfully ✓"
}

# Deploy secrets
deploy_secrets() {
    log "Deploying secrets..."
    
    # Check if secret files exist
    if [ ! -f "k8s/secrets/api-gateway.yaml" ]; then
        warn "k8s/secrets/api-gateway.yaml not found. Please create from template."
        warn "Run: cp k8s/secrets/templates/api-gateway.yaml.template k8s/secrets/api-gateway.yaml"
        warn "Then edit with actual secret values."
        return 1
    fi
    
    if [ ! -f "k8s/secrets/database.yaml" ]; then
        warn "k8s/secrets/database.yaml not found. Please create from template."
        warn "Run: cp k8s/secrets/templates/database.yaml.template k8s/secrets/database.yaml"
        warn "Then edit with actual secret values."
        return 1
    fi
    
    # Apply secrets
    kubectl apply -f k8s/secrets/ --timeout=$KUBECTL_TIMEOUT
    
    log "Secrets deployed successfully ✓"
}

# Deploy ConfigMaps
deploy_configmaps() {
    log "Deploying ConfigMaps..."
    
    kubectl apply -f k8s/configmaps/ --timeout=$KUBECTL_TIMEOUT
    
    log "ConfigMaps deployed successfully ✓"
}

# Deploy services
deploy_services() {
    log "Deploying services..."
    
    kubectl apply -f k8s/services/ --timeout=$KUBECTL_TIMEOUT
    
    log "Services deployed successfully ✓"
}

# Deploy applications
deploy_applications() {
    log "Deploying applications..."
    
    # Deploy in order: database first, then applications
    kubectl apply -f k8s/deployments/database.yaml --timeout=$KUBECTL_TIMEOUT
    kubectl apply -f k8s/deployments/redis.yaml --timeout=$KUBECTL_TIMEOUT
    
    # Wait for databases to be ready
    kubectl wait --for=condition=available deployment/ainflue-database -n $NAMESPACE --timeout=$KUBECTL_TIMEOUT
    kubectl wait --for=condition=available deployment/ainflue-redis -n $NAMESPACE --timeout=$KUBECTL_TIMEOUT
    
    # Deploy application services
    kubectl apply -f k8s/deployments/ai-engine.yaml --timeout=$KUBECTL_TIMEOUT
    kubectl apply -f k8s/deployments/api-gateway.yaml --timeout=$KUBECTL_TIMEOUT
    
    # Wait for applications to be ready
    kubectl wait --for=condition=available deployment/ainflue-ai-engine -n $NAMESPACE --timeout=$KUBECTL_TIMEOUT
    kubectl wait --for=condition=available deployment/ainflue-api-gateway -n $NAMESPACE --timeout=$KUBECTL_TIMEOUT
    
    log "Applications deployed successfully ✓"
}

# Deploy HPA
deploy_hpa() {
    log "Deploying Horizontal Pod Autoscalers..."
    
    kubectl apply -f k8s/hpa/ --timeout=$KUBECTL_TIMEOUT
    
    log "HPA deployed successfully ✓"
}

# Deploy ingress
deploy_ingress() {
    log "Deploying ingress..."
    
    kubectl apply -f k8s/ingress.yaml --timeout=$KUBECTL_TIMEOUT
    
    log "Ingress deployed successfully ✓"
}

# Deploy monitoring stack
deploy_monitoring() {
    log "Deploying monitoring stack..."
    
    # Deploy Prometheus
    kubectl apply -f monitoring/prometheus-config.yaml --timeout=$KUBECTL_TIMEOUT
    
    # Deploy Elasticsearch and Logstash
    kubectl apply -f monitoring/elasticsearch-config.yaml --timeout=$KUBECTL_TIMEOUT
    
    # Deploy Jaeger
    kubectl apply -f monitoring/jaeger-config.yaml --timeout=$KUBECTL_TIMEOUT
    
    # Deploy alerting rules
    kubectl create configmap prometheus-alerts --from-file=monitoring/alerting-rules.yaml -n $MONITORING_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    log "Monitoring stack deployed successfully ✓"
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    # Check pod status
    echo "=== Pod Status ==="
    kubectl get pods -n $NAMESPACE -o wide
    kubectl get pods -n $MONITORING_NAMESPACE -o wide
    
    # Check service status
    echo "=== Service Status ==="
    kubectl get services -n $NAMESPACE
    kubectl get services -n $MONITORING_NAMESPACE
    
    # Check ingress status
    echo "=== Ingress Status ==="
    kubectl get ingress -n $NAMESPACE
    kubectl get ingress -n $MONITORING_NAMESPACE
    
    # Check HPA status
    echo "=== HPA Status ==="
    kubectl get hpa -n $NAMESPACE
    
    # Check for any failing pods
    FAILING_PODS=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running -o name 2>/dev/null | wc -l)
    if [ "$FAILING_PODS" -gt 0 ]; then
        warn "Found $FAILING_PODS non-running pods in namespace $NAMESPACE"
        kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running
    fi
    
    log "Deployment verification completed ✓"
}

# Cleanup function
cleanup() {
    log "Cleaning up deployment..."
    
    read -p "Are you sure you want to delete all Ainflue resources? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        kubectl delete namespace $NAMESPACE --timeout=$KUBECTL_TIMEOUT || true
        log "Cleanup completed ✓"
    else
        log "Cleanup cancelled"
    fi
}

# Show usage
usage() {
    echo "Ainflue Platform Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy     - Deploy the complete platform"
    echo "  verify     - Verify the deployment status"
    echo "  cleanup    - Remove all platform resources"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy      # Deploy everything"
    echo "  $0 verify      # Check deployment status"
    echo "  $0 cleanup     # Remove all resources"
}

# Main deployment function
deploy_all() {
    log "Starting Ainflue Platform deployment..."
    
    check_prerequisites
    create_namespaces
    
    # Try to deploy secrets, continue if templates are used
    if ! deploy_secrets; then
        warn "Secrets deployment skipped. Using default values."
        warn "Make sure to update secrets after deployment for production use."
    fi
    
    deploy_configmaps
    deploy_services
    deploy_applications
    deploy_hpa
    deploy_ingress
    deploy_monitoring
    
    verify_deployment
    
    log "🎉 Ainflue Platform deployment completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Update secrets with production values"
    echo "2. Configure DNS for your ingress domains"  
    echo "3. Set up SSL certificates"
    echo "4. Configure monitoring alerts"
    echo ""
    echo "Access URLs (update with your actual domains):"
    echo "- Platform: https://ainflue.com"
    echo "- API: https://api.ainflue.com"
    echo "- Monitoring: https://monitoring.ainflue.com"
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        deploy_all
        ;;
    verify)
        verify_deployment
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        echo "Unknown command: $1"
        usage
        exit 1
        ;;
esac