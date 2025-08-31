#!/bin/bash
# Ainflue Production Setup Script
# Author: Fahed Mlaiel (mlaiel@live.de)
# 
# This script sets up the production environment for Ainflue platform

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="ainflue"
MONITORING_NAMESPACE="ainflue-monitoring"

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE} AINFLUE PRODUCTION DEPLOYMENT SETUP${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
    
    # Check required tools
    local required_tools=("kubectl" "docker" "python3" "openssl")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            print_error "$tool is not installed"
            exit 1
        fi
    done
    
    # Check kubectl connectivity
    if ! kubectl cluster-info &> /dev/null; then
        print_error "kubectl cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

validate_security() {
    print_step "Validating security configuration..."
    
    if [[ ! -f ".env.production" ]]; then
        print_error ".env.production file not found"
        exit 1
    fi
    
    # Run security validation
    if python3 scripts/validate_production_security.py --env-file .env.production; then
        print_success "Security validation passed"
    else
        print_error "Security validation failed"
        exit 1
    fi
}

create_namespaces() {
    print_step "Creating Kubernetes namespaces..."
    
    # Create main namespace
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Create monitoring namespace
    kubectl create namespace "$MONITORING_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Label namespaces
    kubectl label namespace "$NAMESPACE" app=ainflue env=production --overwrite
    kubectl label namespace "$MONITORING_NAMESPACE" app=ainflue-monitoring env=production --overwrite
    
    print_success "Namespaces created successfully"
}

setup_secrets() {
    print_step "Setting up Kubernetes secrets..."
    
    # Check if secrets file exists
    if [[ ! -f "kubernetes/secrets/production-secrets.yaml" ]]; then
        print_error "Production secrets file not found"
        exit 1
    fi
    
    # Prompt for secret values if they contain placeholders
    print_warning "Please ensure all placeholder values in kubernetes/secrets/production-secrets.yaml are replaced with actual secrets"
    read -p "Have you replaced all placeholder values? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Please replace placeholder values before continuing"
        exit 1
    fi
    
    # Apply secrets
    kubectl apply -f kubernetes/secrets/production-secrets.yaml -n "$NAMESPACE"
    
    print_success "Secrets applied successfully"
}

setup_monitoring() {
    print_step "Setting up monitoring stack..."
    
    # Create monitoring ConfigMaps
    kubectl create configmap prometheus-config \
        --from-file=monitoring/prometheus/prometheus.yml \
        --from-file=monitoring/prometheus/production_alert_rules.yml \
        -n "$MONITORING_NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create Grafana dashboard ConfigMap
    kubectl create configmap grafana-dashboards \
        --from-file=monitoring/grafana/ \
        -n "$MONITORING_NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    print_success "Monitoring configuration applied"
}

deploy_database() {
    print_step "Deploying database cluster..."
    
    # Deploy PostgreSQL cluster
    if [[ -f "kubernetes/database/postgresql-cluster.yaml" ]]; then
        kubectl apply -f kubernetes/database/postgresql-cluster.yaml -n "$NAMESPACE"
    fi
    
    # Deploy Redis cluster
    if [[ -f "kubernetes/database/redis-cluster.yaml" ]]; then
        kubectl apply -f kubernetes/database/redis-cluster.yaml -n "$NAMESPACE"
    fi
    
    # Deploy MongoDB replica set
    if [[ -f "kubernetes/database/mongodb-replicaset.yaml" ]]; then
        kubectl apply -f kubernetes/database/mongodb-replicaset.yaml -n "$NAMESPACE"
    fi
    
    print_success "Database cluster deployment initiated"
}

deploy_application() {
    print_step "Deploying application services..."
    
    # Deploy main application
    if [[ -d "kubernetes/environments/production" ]]; then
        kubectl apply -f kubernetes/environments/production/ -n "$NAMESPACE"
    fi
    
    print_success "Application deployment initiated"
}

deploy_monitoring_stack() {
    print_step "Deploying monitoring stack..."
    
    # Deploy using docker-compose in monitoring mode
    if [[ -f "docker-compose.monitoring.yml" ]]; then
        print_warning "Monitoring stack should be deployed separately using docker-compose or Helm"
        print_warning "Run: docker-compose -f docker-compose.monitoring.yml up -d"
    fi
    
    print_success "Monitoring deployment instructions provided"
}

wait_for_deployments() {
    print_step "Waiting for deployments to be ready..."
    
    # Wait for database deployments
    local db_deployments=("postgresql-master" "redis-master" "mongodb-primary")
    for deployment in "${db_deployments[@]}"; do
        if kubectl get deployment "$deployment" -n "$NAMESPACE" &> /dev/null; then
            print_step "Waiting for $deployment..."
            kubectl rollout status deployment/"$deployment" -n "$NAMESPACE" --timeout=600s
        fi
    done
    
    # Wait for application deployments
    local app_deployments=("ainflue-api" "ainflue-crawler" "ainflue-ai")
    for deployment in "${app_deployments[@]}"; do
        if kubectl get deployment "$deployment" -n "$NAMESPACE" &> /dev/null; then
            print_step "Waiting for $deployment..."
            kubectl rollout status deployment/"$deployment" -n "$NAMESPACE" --timeout=600s
        fi
    done
    
    print_success "All deployments are ready"
}

run_health_checks() {
    print_step "Running health checks..."
    
    # Get service endpoints
    API_SERVICE=$(kubectl get service ainflue-api -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    
    if [[ -n "$API_SERVICE" ]]; then
        # Test API health endpoint
        if curl -f "http://$API_SERVICE/health" &> /dev/null; then
            print_success "API health check passed"
        else
            print_warning "API health check failed - service may still be starting"
        fi
    else
        print_warning "API service not yet available"
    fi
    
    print_success "Health checks completed"
}

generate_summary() {
    print_step "Generating deployment summary..."
    
    echo ""
    echo -e "${BLUE}DEPLOYMENT SUMMARY${NC}"
    echo "===================="
    
    # Show namespace status
    echo "Namespaces:"
    kubectl get namespaces | grep -E "(ainflue|monitoring)"
    echo ""
    
    # Show pod status
    echo "Pods in $NAMESPACE:"
    kubectl get pods -n "$NAMESPACE" -o wide
    echo ""
    
    # Show services
    echo "Services in $NAMESPACE:"
    kubectl get services -n "$NAMESPACE"
    echo ""
    
    # Show secrets
    echo "Secrets in $NAMESPACE:"
    kubectl get secrets -n "$NAMESPACE"
    echo ""
    
    print_success "Production deployment completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Configure DNS to point to your LoadBalancer IPs"
    echo "2. Set up SSL certificates"
    echo "3. Configure monitoring alerts"
    echo "4. Run integration tests"
    echo "5. Set up backup procedures"
}

cleanup_on_error() {
    print_error "Deployment failed. Cleaning up..."
    
    # Optionally clean up partial deployments
    read -p "Do you want to clean up the failed deployment? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
        kubectl delete namespace "$MONITORING_NAMESPACE" --ignore-not-found=true
        print_success "Cleanup completed"
    fi
}

main() {
    print_header
    
    # Set up error handling
    trap cleanup_on_error ERR
    
    # Run deployment steps
    check_prerequisites
    validate_security
    create_namespaces
    setup_secrets
    setup_monitoring
    deploy_database
    deploy_application
    deploy_monitoring_stack
    wait_for_deployments
    run_health_checks
    generate_summary
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-validation    Skip security validation"
            echo "  --namespace NAME     Use custom namespace (default: ainflue)"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main "$@"