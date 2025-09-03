#!/bin/bash

# =================================================================
# Ainflue Platform Monitoring Management Script
# Author: Fahed Mlaiel (mlaiel@live.de)
# Description: Complete monitoring system management for Ainflue Platform
# Usage: ./scripts/monitoring.sh [command] [options]
# =================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${ENVIRONMENT:-production}"
NAMESPACE="ainflue-monitoring"
MONITORING_DIR="$PROJECT_ROOT/monitoring"
KUBERNETES_DIR="$PROJECT_ROOT/kubernetes/monitoring"

# Logging functions
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

header() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}========================================${NC}"
}

# Check if monitoring stack is deployed
check_monitoring_status() {
    log "Checking monitoring stack status..."
    
    local status="unknown"
    if kubectl get namespace $NAMESPACE &>/dev/null; then
        local pods_ready=$(kubectl get pods -n $NAMESPACE --no-headers | grep -c "Running" || echo "0")
        local total_pods=$(kubectl get pods -n $NAMESPACE --no-headers | wc -l || echo "0")
        
        if [[ $pods_ready -eq $total_pods && $total_pods -gt 0 ]]; then
            status="healthy"
            success "Monitoring stack is healthy ($pods_ready/$total_pods pods running)"
        elif [[ $total_pods -gt 0 ]]; then
            status="degraded"
            warning "Monitoring stack is degraded ($pods_ready/$total_pods pods running)"
        else
            status="failed"
            error "Monitoring stack is deployed but no pods found"
        fi
    else
        status="not_deployed"
        log "Monitoring stack is not deployed"
    fi
    
    echo "$status"
}

# Deploy monitoring stack
deploy_monitoring() {
    header "Deploying Monitoring Stack"
    
    log "Running monitoring deployment script..."
    if [[ -x "$SCRIPT_DIR/deploy-monitoring.sh" ]]; then
        "$SCRIPT_DIR/deploy-monitoring.sh"
        success "Monitoring stack deployed successfully"
    else
        error "Deploy monitoring script not found or not executable"
        return 1
    fi
}

# Stop monitoring stack
stop_monitoring() {
    header "Stopping Monitoring Stack"
    
    log "Stopping monitoring services..."
    if kubectl get namespace $NAMESPACE &>/dev/null; then
        kubectl delete namespace $NAMESPACE
        success "Monitoring stack stopped"
    else
        warning "Monitoring stack was not running"
    fi
}

# Restart monitoring stack
restart_monitoring() {
    header "Restarting Monitoring Stack"
    
    log "Restarting monitoring services..."
    stop_monitoring
    sleep 10
    deploy_monitoring
}

# Show monitoring status
show_status() {
    header "Monitoring Stack Status"
    
    local status=$(check_monitoring_status)
    
    echo ""
    echo "Overall Status: $status"
    echo ""
    
    if kubectl get namespace $NAMESPACE &>/dev/null; then
        echo "Namespace: $NAMESPACE"
        echo ""
        
        echo "Services:"
        kubectl get services -n $NAMESPACE -o wide
        echo ""
        
        echo "Pods:"
        kubectl get pods -n $NAMESPACE -o wide
        echo ""
        
        echo "Persistent Volumes:"
        kubectl get pvc -n $NAMESPACE
        echo ""
        
        # Show resource usage
        echo "Resource Usage:"
        kubectl top pods -n $NAMESPACE 2>/dev/null || echo "Metrics server not available"
    else
        echo "Monitoring stack is not deployed"
    fi
}

# Show monitoring access information
show_access() {
    header "Monitoring Access Information"
    
    if ! kubectl get namespace $NAMESPACE &>/dev/null; then
        error "Monitoring stack is not deployed"
        return 1
    fi
    
    echo ""
    echo "📊 Access URLs (use port-forward if LoadBalancer not available):"
    echo ""
    
    # Check for LoadBalancer IPs
    local grafana_ip=$(kubectl get service grafana -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    local prometheus_ip=$(kubectl get service prometheus -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    
    if [[ -n "$grafana_ip" ]]; then
        echo "🌐 Grafana:        http://$grafana_ip:3000"
        echo "🌐 Prometheus:     http://$prometheus_ip:9090"
        echo "🌐 AlertManager:   http://$prometheus_ip:9093"
    else
        echo "📱 Port-forward commands (run in separate terminals):"
        echo ""
        echo "   Grafana:       kubectl port-forward -n $NAMESPACE service/grafana 3000:3000"
        echo "   Prometheus:    kubectl port-forward -n $NAMESPACE service/prometheus 9090:9090"
        echo "   AlertManager:  kubectl port-forward -n $NAMESPACE service/alertmanager 9093:9093"
        echo "   Jaeger:        kubectl port-forward -n $NAMESPACE service/jaeger 16686:16686"
        echo "   Kibana:        kubectl port-forward -n $NAMESPACE service/kibana 5601:5601"
        echo ""
        echo "Then access via:"
        echo "   Grafana:       http://localhost:3000"
        echo "   Prometheus:    http://localhost:9090"
        echo "   AlertManager:  http://localhost:9093"
        echo "   Jaeger:        http://localhost:16686"
        echo "   Kibana:        http://localhost:5601"
    fi
    
    echo ""
    echo "🔐 Default Credentials:"
    echo "   Grafana - Username: admin, Password: admin123"
    echo "   Kibana - Username: elastic, Password: check secrets"
    echo ""
}

# Show logs for monitoring components
show_logs() {
    local component="${1:-all}"
    
    header "Monitoring Logs - $component"
    
    if ! kubectl get namespace $NAMESPACE &>/dev/null; then
        error "Monitoring stack is not deployed"
        return 1
    fi
    
    case $component in
        "grafana")
            kubectl logs -n $NAMESPACE deployment/grafana --tail=50
            ;;
        "prometheus")
            kubectl logs -n $NAMESPACE deployment/prometheus --tail=50
            ;;
        "alertmanager")
            kubectl logs -n $NAMESPACE deployment/alertmanager --tail=50
            ;;
        "elasticsearch")
            kubectl logs -n $NAMESPACE deployment/elasticsearch --tail=50
            ;;
        "kibana")
            kubectl logs -n $NAMESPACE deployment/kibana --tail=50
            ;;
        "all")
            log "Getting logs from all monitoring components..."
            echo ""
            echo "=== Grafana Logs ==="
            kubectl logs -n $NAMESPACE deployment/grafana --tail=20 2>/dev/null || echo "Grafana not found"
            echo ""
            echo "=== Prometheus Logs ==="
            kubectl logs -n $NAMESPACE deployment/prometheus --tail=20 2>/dev/null || echo "Prometheus not found"
            echo ""
            echo "=== AlertManager Logs ==="
            kubectl logs -n $NAMESPACE deployment/alertmanager --tail=20 2>/dev/null || echo "AlertManager not found"
            ;;
        *)
            error "Unknown component: $component"
            echo "Available components: grafana, prometheus, alertmanager, elasticsearch, kibana, all"
            return 1
            ;;
    esac
}

# Health check for monitoring stack
health_check() {
    header "Monitoring Stack Health Check"
    
    local overall_health="healthy"
    
    if ! kubectl get namespace $NAMESPACE &>/dev/null; then
        error "❌ Namespace not found"
        overall_health="failed"
    else
        success "✅ Namespace exists"
    fi
    
    # Check each component
    local components=("grafana" "prometheus" "alertmanager")
    
    for component in "${components[@]}"; do
        if kubectl get deployment $component -n $NAMESPACE &>/dev/null; then
            local ready=$(kubectl get deployment $component -n $NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
            local desired=$(kubectl get deployment $component -n $NAMESPACE -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "1")
            
            if [[ "$ready" == "$desired" && "$ready" -gt 0 ]]; then
                success "✅ $component is healthy ($ready/$desired replicas)"
            else
                error "❌ $component is unhealthy ($ready/$desired replicas)"
                overall_health="degraded"
            fi
        else
            error "❌ $component deployment not found"
            overall_health="failed"
        fi
    done
    
    # Check persistent volumes
    local pvc_count=$(kubectl get pvc -n $NAMESPACE --no-headers 2>/dev/null | wc -l || echo "0")
    local bound_pvc=$(kubectl get pvc -n $NAMESPACE --no-headers 2>/dev/null | grep -c "Bound" || echo "0")
    
    if [[ "$pvc_count" -eq "$bound_pvc" && "$pvc_count" -gt 0 ]]; then
        success "✅ Storage is healthy ($bound_pvc/$pvc_count PVCs bound)"
    else
        warning "⚠️  Storage issues detected ($bound_pvc/$pvc_count PVCs bound)"
        overall_health="degraded"
    fi
    
    echo ""
    case $overall_health in
        "healthy")
            success "🟢 Overall Health: HEALTHY"
            ;;
        "degraded")
            warning "🟡 Overall Health: DEGRADED"
            ;;
        "failed")
            error "🔴 Overall Health: FAILED"
            ;;
    esac
}

# Update monitoring configuration
update_config() {
    header "Updating Monitoring Configuration"
    
    log "Updating Prometheus configuration..."
    if [[ -f "$MONITORING_DIR/prometheus/prometheus.yml" ]]; then
        kubectl create configmap prometheus-config \
            --from-file="$MONITORING_DIR/prometheus/prometheus.yml" \
            -n $NAMESPACE \
            --dry-run=client -o yaml | kubectl apply -f -
        success "Prometheus configuration updated"
    else
        warning "Prometheus configuration file not found"
    fi
    
    log "Updating AlertManager configuration..."
    if [[ -f "$MONITORING_DIR/alertmanager/alertmanager.yml" ]]; then
        kubectl create configmap alertmanager-config \
            --from-file="$MONITORING_DIR/alertmanager/alertmanager.yml" \
            -n $NAMESPACE \
            --dry-run=client -o yaml | kubectl apply -f -
        success "AlertManager configuration updated"
    else
        warning "AlertManager configuration file not found"
    fi
    
    log "Restarting monitoring pods to apply new configuration..."
    kubectl rollout restart deployment/prometheus -n $NAMESPACE 2>/dev/null || true
    kubectl rollout restart deployment/alertmanager -n $NAMESPACE 2>/dev/null || true
    
    success "Configuration update completed"
}

# Run monitoring tests
run_tests() {
    header "Running Monitoring Tests"
    
    if [[ -x "$SCRIPT_DIR/test-monitoring.sh" ]]; then
        "$SCRIPT_DIR/test-monitoring.sh"
    else
        error "Test monitoring script not found or not executable"
        return 1
    fi
}

# Show usage information
show_usage() {
    cat << EOF
Usage: $0 <command> [options]

Commands:
    deploy          Deploy the monitoring stack
    stop            Stop the monitoring stack
    restart         Restart the monitoring stack
    status          Show monitoring stack status
    access          Show access information and URLs
    logs [component] Show logs (components: grafana, prometheus, alertmanager, all)
    health          Perform health check
    update-config   Update monitoring configuration
    test            Run monitoring tests
    help            Show this help message

Options:
    --environment ENV    Environment (default: production)
    --namespace NS       Kubernetes namespace (default: ainflue-monitoring)

Examples:
    $0 deploy
    $0 status
    $0 logs grafana
    $0 health
    $0 access

Environment Variables:
    ENVIRONMENT          Deployment environment
    NAMESPACE           Kubernetes namespace for monitoring

EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                break
                ;;
        esac
    done
}

# Main function
main() {
    local command="${1:-help}"
    shift || true
    
    case $command in
        "deploy")
            deploy_monitoring
            ;;
        "stop")
            stop_monitoring
            ;;
        "restart")
            restart_monitoring
            ;;
        "status")
            show_status
            ;;
        "access")
            show_access
            ;;
        "logs")
            show_logs "${1:-all}"
            ;;
        "health")
            health_check
            ;;
        "update-config")
            update_config
            ;;
        "test")
            run_tests
            ;;
        "help"|"--help"|"-h")
            show_usage
            ;;
        *)
            error "Unknown command: $command"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    parse_arguments "$@"
    main "$@"
fi