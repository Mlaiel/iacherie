#!/bin/bash

# Ainflue Monitoring Stack Deployment Script
# Author: Fahed Mlaiel <mlaiel@live.de>
# Complete deployment of monitoring and observability infrastructure

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="ainflue-monitoring"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITORING_DIR="$(dirname "$SCRIPT_DIR")/monitoring"
KUBERNETES_DIR="$(dirname "$SCRIPT_DIR")/kubernetes/monitoring"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check if helm is installed (optional)
    if ! command -v helm &> /dev/null; then
        warning "helm is not installed. Some features may not be available."
    fi
    
    # Check if cluster is accessible
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    success "Prerequisites check completed"
}

# Create namespace
create_namespace() {
    log "Creating namespace ${NAMESPACE}..."
    
    if kubectl get namespace ${NAMESPACE} &> /dev/null; then
        warning "Namespace ${NAMESPACE} already exists"
    else
        kubectl create namespace ${NAMESPACE}
        kubectl label namespace ${NAMESPACE} name=${NAMESPACE}
        success "Namespace ${NAMESPACE} created"
    fi
}

# Deploy monitoring stack
deploy_monitoring_stack() {
    log "Deploying monitoring stack..."
    
    # Deploy RBAC and storage first
    log "Deploying RBAC and storage configurations..."
    kubectl apply -f "${KUBERNETES_DIR}/monitoring-rbac-storage.yaml"
    
    # Wait for PVCs to be bound
    log "Waiting for PVCs to be bound..."
    kubectl wait --for=condition=Bound pvc --all -n ${NAMESPACE} --timeout=300s || true
    
    # Deploy main monitoring stack
    log "Deploying main monitoring stack..."
    kubectl apply -f "${KUBERNETES_DIR}/monitoring-stack.yaml"
    
    # Deploy Filebeat for log collection
    log "Deploying Filebeat for log collection..."
    kubectl apply -f "${KUBERNETES_DIR}/filebeat.yaml"
    
    success "Monitoring stack deployed"
}

# Deploy alert rules
deploy_alert_rules() {
    log "Deploying Prometheus alert rules..."
    
    # Create configmap for SLA alerts
    kubectl create configmap prometheus-sla-rules \
        --from-file="${MONITORING_DIR}/prometheus/sla_alerts.yml" \
        -n ${NAMESPACE} \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create configmap for existing alert rules
    if [ -f "${MONITORING_DIR}/prometheus/alert_rules.yml" ]; then
        kubectl create configmap prometheus-alert-rules \
            --from-file="${MONITORING_DIR}/prometheus/alert_rules.yml" \
            -n ${NAMESPACE} \
            --dry-run=client -o yaml | kubectl apply -f -
    fi
    
    success "Alert rules deployed"
}

# Wait for deployments to be ready
wait_for_deployments() {
    log "Waiting for deployments to be ready..."
    
    local deployments=(
        "prometheus"
        "grafana"
        "alertmanager"
        "jaeger"
        "elasticsearch"
        "kibana"
        "logstash"
    )
    
    for deployment in "${deployments[@]}"; do
        log "Waiting for ${deployment} to be ready..."
        kubectl rollout status deployment/${deployment} -n ${NAMESPACE} --timeout=300s
        success "${deployment} is ready"
    done
    
    # Wait for DaemonSet (Filebeat)
    log "Waiting for Filebeat DaemonSet to be ready..."
    kubectl rollout status daemonset/filebeat -n ${NAMESPACE} --timeout=300s
    success "Filebeat is ready"
}

# Configure ingress
configure_ingress() {
    log "Configuring ingress for monitoring services..."
    
    # Check if ingress-nginx is installed
    if kubectl get namespace ingress-nginx &> /dev/null; then
        log "ingress-nginx found, configuring ingress..."
        # Ingress is already configured in monitoring-rbac-storage.yaml
        success "Ingress configuration applied"
    else
        warning "ingress-nginx not found. You may need to configure ingress manually."
    fi
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring configuration..."
    
    # Create AlertManager configuration
    kubectl create configmap alertmanager-config \
        --from-file="${MONITORING_DIR}/alertmanager/alertmanager.yml" \
        -n ${NAMESPACE} \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create Filebeat configuration
    kubectl create configmap filebeat-config \
        --from-file="${MONITORING_DIR}/filebeat/filebeat.yml" \
        -n ${NAMESPACE} \
        --dry-run=client -o yaml | kubectl apply -f -
    
    success "Monitoring configuration setup completed"
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    # Check pod status
    log "Checking pod status in namespace ${NAMESPACE}..."
    kubectl get pods -n ${NAMESPACE}
    
    # Check services
    log "Checking services in namespace ${NAMESPACE}..."
    kubectl get services -n ${NAMESPACE}
    
    # Check ingress
    log "Checking ingress in namespace ${NAMESPACE}..."
    kubectl get ingress -n ${NAMESPACE} || warning "No ingress found"
    
    # Check persistent volumes
    log "Checking persistent volume claims..."
    kubectl get pvc -n ${NAMESPACE}
    
    success "Deployment verification completed"
}

# Display access information
display_access_info() {
    log "Monitoring stack access information:"
    
    echo ""
    echo "==================== ACCESS INFORMATION ===================="
    echo ""
    
    # Get LoadBalancer IPs or NodePort info
    local grafana_service=$(kubectl get service grafana -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    local prometheus_service=$(kubectl get service prometheus -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    
    if [[ -n "$grafana_service" ]]; then
        echo "🌐 Grafana:        http://${grafana_service}:3000"
        echo "🌐 Prometheus:     http://${prometheus_service}:9090"
    else
        echo "📱 To access services, use port-forward:"
        echo ""
        echo "   Grafana:       kubectl port-forward -n ${NAMESPACE} service/grafana 3000:3000"
        echo "   Prometheus:    kubectl port-forward -n ${NAMESPACE} service/prometheus 9090:9090"
        echo "   AlertManager:  kubectl port-forward -n ${NAMESPACE} service/alertmanager 9093:9093"
        echo "   Jaeger UI:     kubectl port-forward -n ${NAMESPACE} service/jaeger 16686:16686"
        echo "   Kibana:        kubectl port-forward -n ${NAMESPACE} service/kibana 5601:5601"
    fi
    
    echo ""
    echo "🔐 Default Grafana credentials:"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo ""
    echo "📊 Available dashboards:"
    echo "   - System Overview"
    echo "   - AI Models Performance"
    echo "   - Database Performance"
    echo "   - Business Metrics"
    echo ""
    echo "🚨 Alert destinations:"
    echo "   - Email: Configure SMTP_PASSWORD environment variable"
    echo "   - Slack: Configure SLACK_WEBHOOK_URL environment variable"
    echo "   - SMS: Configure SMS_WEBHOOK_URL and SMS_API_TOKEN environment variables"
    echo ""
    echo "============================================================="
}

# Cleanup function
cleanup() {
    if [[ "${1:-}" == "--cleanup" ]]; then
        log "Cleaning up monitoring stack..."
        
        kubectl delete namespace ${NAMESPACE} --ignore-not-found=true
        
        success "Cleanup completed"
        exit 0
    fi
}

# Main execution
main() {
    log "Starting Ainflue Monitoring Stack Deployment"
    log "============================================="
    
    # Handle cleanup option
    cleanup "$@"
    
    # Main deployment steps
    check_prerequisites
    create_namespace
    setup_monitoring
    deploy_monitoring_stack
    deploy_alert_rules
    configure_ingress
    
    log "Waiting for services to be ready..."
    sleep 30
    
    wait_for_deployments
    verify_deployment
    display_access_info
    
    success "Monitoring stack deployment completed successfully!"
    log "Check the services with: kubectl get all -n ${NAMESPACE}"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--cleanup]"
        echo ""
        echo "Deploy the complete Ainflue monitoring stack including:"
        echo "  - Prometheus for metrics collection"
        echo "  - Grafana for visualization"
        echo "  - AlertManager for alerting"
        echo "  - Jaeger for distributed tracing"
        echo "  - ELK Stack for log aggregation"
        echo "  - Filebeat for log collection"
        echo ""
        echo "Options:"
        echo "  --cleanup    Remove the monitoring stack"
        echo "  --help, -h   Show this help message"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac