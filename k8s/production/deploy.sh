#!/bin/bash

# Ainflue Production Deployment Script
# Automated deployment for Kubernetes production environment
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="ainflue-production"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST_DIR="${SCRIPT_DIR}"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        log_info "Please ensure kubectl is configured correctly"
        exit 1
    fi
    
    # Check cert-manager
    if ! kubectl get crd certificates.cert-manager.io &> /dev/null; then
        log_warning "cert-manager CRDs not found"
        log_info "SSL certificates will need to be managed manually"
    fi
    
    # Check ingress controller
    if ! kubectl get pods -n ingress-nginx &> /dev/null; then
        log_warning "nginx-ingress-controller namespace not found"
        log_info "Please ensure nginx ingress controller is installed"
    fi
    
    log_success "Prerequisites check completed"
}

create_namespace() {
    log_info "Creating namespace: ${NAMESPACE}"
    
    if kubectl get namespace ${NAMESPACE} &> /dev/null; then
        log_warning "Namespace ${NAMESPACE} already exists"
    else
        kubectl create namespace ${NAMESPACE}
        log_success "Namespace ${NAMESPACE} created"
    fi
    
    # Label namespace for monitoring
    kubectl label namespace ${NAMESPACE} name=${NAMESPACE} --overwrite
    kubectl label namespace ${NAMESPACE} environment=production --overwrite
}

deploy_secrets() {
    log_info "Deploying secrets..."
    
    if [[ -f "${MANIFEST_DIR}/secrets.yaml" ]]; then
        kubectl apply -f "${MANIFEST_DIR}/secrets.yaml"
        log_success "Secrets deployed"
    else
        log_error "secrets.yaml not found"
        exit 1
    fi
}

deploy_configmaps() {
    log_info "Deploying ConfigMaps..."
    
    if [[ -f "${MANIFEST_DIR}/configmaps.yaml" ]]; then
        kubectl apply -f "${MANIFEST_DIR}/configmaps.yaml"
        log_success "ConfigMaps deployed"
    else
        log_error "configmaps.yaml not found"
        exit 1
    fi
}

deploy_services() {
    log_info "Deploying Services..."
    
    if [[ -f "${MANIFEST_DIR}/services.yaml" ]]; then
        kubectl apply -f "${MANIFEST_DIR}/services.yaml"
        log_success "Services deployed"
    else
        log_error "services.yaml not found"
        exit 1
    fi
}

deploy_applications() {
    log_info "Deploying Applications..."
    
    if [[ -f "${MANIFEST_DIR}/deployments.yaml" ]]; then
        kubectl apply -f "${MANIFEST_DIR}/deployments.yaml"
        log_success "Applications deployed"
        
        # Wait for deployments to be ready
        log_info "Waiting for deployments to be ready..."
        kubectl wait --for=condition=available --timeout=300s deployment -l environment=production -n ${NAMESPACE}
        log_success "All deployments are ready"
    else
        log_error "deployments.yaml not found"
        exit 1
    fi
}

deploy_network_policies() {
    log_info "Deploying Network Policies..."
    
    if [[ -f "${MANIFEST_DIR}/networkpolicies.yaml" ]]; then
        kubectl apply -f "${MANIFEST_DIR}/networkpolicies.yaml"
        log_success "Network Policies deployed"
    else
        log_warning "networkpolicies.yaml not found, skipping network policies"
    fi
}

deploy_ingress() {
    log_info "Deploying Ingress..."
    
    if [[ -f "${MANIFEST_DIR}/ingress.yaml" ]]; then
        kubectl apply -f "${MANIFEST_DIR}/ingress.yaml"
        log_success "Ingress deployed"
        
        # Wait for ingress to get an IP
        log_info "Waiting for ingress to get external IP..."
        timeout=60
        while [[ $timeout -gt 0 ]]; do
            if kubectl get ingress -n ${NAMESPACE} -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' &> /dev/null; then
                EXTERNAL_IP=$(kubectl get ingress -n ${NAMESPACE} -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')
                log_success "Ingress external IP: ${EXTERNAL_IP}"
                break
            fi
            sleep 2
            timeout=$((timeout-2))
        done
        
        if [[ $timeout -le 0 ]]; then
            log_warning "Ingress IP not assigned yet, check manually later"
        fi
    else
        log_error "ingress.yaml not found"
        exit 1
    fi
}

deploy_autoscaling() {
    log_info "Deploying Horizontal Pod Autoscalers..."
    
    if [[ -f "${MANIFEST_DIR}/hpa.yaml" ]]; then
        kubectl apply -f "${MANIFEST_DIR}/hpa.yaml"
        log_success "HPAs deployed"
    else
        log_warning "hpa.yaml not found, skipping autoscaling"
    fi
}

deploy_disruption_budgets() {
    log_info "Deploying Pod Disruption Budgets..."
    
    if [[ -f "${MANIFEST_DIR}/pdb.yaml" ]]; then
        kubectl apply -f "${MANIFEST_DIR}/pdb.yaml"
        log_success "PDBs deployed"
    else
        log_warning "pdb.yaml not found, skipping disruption budgets"
    fi
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    echo -e "\n${BLUE}=== Deployment Status ===${NC}"
    kubectl get all -n ${NAMESPACE}
    
    echo -e "\n${BLUE}=== Ingress Status ===${NC}"
    kubectl get ingress -n ${NAMESPACE}
    
    echo -e "\n${BLUE}=== Certificate Status ===${NC}"
    kubectl get certificates -n ${NAMESPACE} 2>/dev/null || log_warning "No certificates found"
    
    echo -e "\n${BLUE}=== HPA Status ===${NC}"
    kubectl get hpa -n ${NAMESPACE} 2>/dev/null || log_warning "No HPAs found"
    
    echo -e "\n${BLUE}=== PDB Status ===${NC}"
    kubectl get pdb -n ${NAMESPACE} 2>/dev/null || log_warning "No PDBs found"
    
    echo -e "\n${BLUE}=== Network Policies ===${NC}"
    kubectl get networkpolicies -n ${NAMESPACE} 2>/dev/null || log_warning "No Network Policies found"
    
    log_success "Deployment verification completed"
}

show_access_info() {
    log_info "Access Information:"
    
    echo -e "\n${GREEN}🌍 Application URLs:${NC}"
    echo "  • Main Site: https://ainflue.com"
    echo "  • Application: https://app.ainflue.com"
    echo "  • API: https://api.ainflue.com"
    echo "  • Static CDN: https://static.ainflue.com"
    echo "  • Monitoring: https://monitoring.ainflue.com"
    
    echo -e "\n${GREEN}📊 Monitoring Commands:${NC}"
    echo "  • Check pods: kubectl get pods -n ${NAMESPACE}"
    echo "  • Check services: kubectl get svc -n ${NAMESPACE}"
    echo "  • Check ingress: kubectl get ingress -n ${NAMESPACE}"
    echo "  • Check logs: kubectl logs -f deployment/ainflue-api -n ${NAMESPACE}"
    echo "  • Check HPA: kubectl get hpa -n ${NAMESPACE}"
    
    echo -e "\n${GREEN}🔧 Useful Commands:${NC}"
    echo "  • Scale deployment: kubectl scale deployment ainflue-api --replicas=5 -n ${NAMESPACE}"
    echo "  • Rolling restart: kubectl rollout restart deployment/ainflue-api -n ${NAMESPACE}"
    echo "  • Check events: kubectl get events -n ${NAMESPACE} --sort-by='.lastTimestamp'"
}

cleanup() {
    if [[ "${1}" == "--confirm" ]]; then
        log_warning "Cleaning up deployment..."
        kubectl delete namespace ${NAMESPACE} --ignore-not-found=true
        log_success "Cleanup completed"
    else
        log_info "To cleanup the deployment, run: $0 cleanup --confirm"
    fi
}

main() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                Ainflue Production Deployment                  ║"
    echo "║                                                               ║"
    echo "║  Author: Fahed Mlaiel <mlaiel@live.de>                       ║"
    echo "║  Copyright: © 2025 Fahed Mlaiel. All rights reserved.        ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
    
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            create_namespace
            deploy_secrets
            deploy_configmaps
            deploy_services
            deploy_applications
            deploy_network_policies
            deploy_ingress
            deploy_autoscaling
            deploy_disruption_budgets
            verify_deployment
            show_access_info
            ;;
        "verify")
            verify_deployment
            show_access_info
            ;;
        "cleanup")
            cleanup "${2}"
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  deploy    Deploy the entire Ainflue production stack (default)"
            echo "  verify    Verify the current deployment status"
            echo "  cleanup   Remove the entire deployment (requires --confirm)"
            echo "  help      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Deploy everything"
            echo "  $0 deploy            # Deploy everything"
            echo "  $0 verify            # Check deployment status"
            echo "  $0 cleanup --confirm # Remove everything"
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"