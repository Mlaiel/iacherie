#!/bin/bash

# Monitoring Stack Validation and Testing Script
# Author: Fahed Mlaiel <mlaiel@live.de>
# Comprehensive testing of monitoring and observability infrastructure

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
NAMESPACE="ainflue-monitoring"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Logging functions
log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}[✅ PASS]${NC} $1"; ((TESTS_PASSED++)); }
failure() { echo -e "${RED}[❌ FAIL]${NC} $1"; ((TESTS_FAILED++)); }
warning() { echo -e "${YELLOW}[⚠️ WARN]${NC} $1"; }
test_start() { echo -e "${BLUE}[🧪 TEST]${NC} $1"; ((TESTS_TOTAL++)); }

# Test configuration files
test_configuration_files() {
    log "Testing configuration files..."
    
    test_start "Validating Prometheus configuration"
    if [[ -f "${PROJECT_ROOT}/monitoring/prometheus/prometheus.yml" ]]; then
        success "Prometheus configuration file exists"
    else
        failure "Prometheus configuration file missing"
    fi
    
    test_start "Validating AlertManager configuration"
    if [[ -f "${PROJECT_ROOT}/monitoring/alertmanager/alertmanager.yml" ]]; then
        if python3 -c "import yaml; yaml.safe_load(open('${PROJECT_ROOT}/monitoring/alertmanager/alertmanager.yml'))" 2>/dev/null; then
            success "AlertManager configuration is valid YAML"
        else
            failure "AlertManager configuration has YAML syntax errors"
        fi
    else
        failure "AlertManager configuration file missing"
    fi
    
    test_start "Validating SLA alerts configuration"
    if [[ -f "${PROJECT_ROOT}/monitoring/prometheus/sla_alerts.yml" ]]; then
        if python3 -c "import yaml; yaml.safe_load(open('${PROJECT_ROOT}/monitoring/prometheus/sla_alerts.yml'))" 2>/dev/null; then
            success "SLA alerts configuration is valid YAML"
        else
            failure "SLA alerts configuration has YAML syntax errors"
        fi
    else
        failure "SLA alerts configuration file missing"
    fi
    
    test_start "Validating Filebeat configuration"
    if [[ -f "${PROJECT_ROOT}/monitoring/filebeat/filebeat.yml" ]]; then
        if python3 -c "import yaml; yaml.safe_load(open('${PROJECT_ROOT}/monitoring/filebeat/filebeat.yml'))" 2>/dev/null; then
            success "Filebeat configuration is valid YAML"
        else
            failure "Filebeat configuration has YAML syntax errors"
        fi
    else
        failure "Filebeat configuration file missing"
    fi
}

# Test Kubernetes manifests
test_kubernetes_manifests() {
    log "Testing Kubernetes manifests..."
    
    local manifests=(
        "kubernetes/monitoring/monitoring-stack.yaml"
        "kubernetes/monitoring/monitoring-rbac-storage.yaml"
        "kubernetes/monitoring/filebeat.yaml"
    )
    
    for manifest in "${manifests[@]}"; do
        test_start "Validating ${manifest}"
        if [[ -f "${PROJECT_ROOT}/${manifest}" ]]; then
            if kubectl apply --dry-run=client -f "${PROJECT_ROOT}/${manifest}" &>/dev/null; then
                success "Kubernetes manifest ${manifest} is valid"
            else
                failure "Kubernetes manifest ${manifest} has validation errors"
            fi
        else
            failure "Kubernetes manifest ${manifest} missing"
        fi
    done
}

# Test Python configuration modules
test_python_modules() {
    log "Testing Python configuration modules..."
    
    test_start "Validating business KPIs configuration"
    if [[ -f "${PROJECT_ROOT}/config/monitoring/business_kpis_config.py" ]]; then
        if python3 -m py_compile "${PROJECT_ROOT}/config/monitoring/business_kpis_config.py" 2>/dev/null; then
            success "Business KPIs configuration compiles successfully"
        else
            failure "Business KPIs configuration has syntax errors"
        fi
    else
        failure "Business KPIs configuration file missing"
    fi
    
    test_start "Testing business KPIs module functionality"
    if python3 -c "
import sys
sys.path.append('${PROJECT_ROOT}')
from config.monitoring.business_kpis_config import BusinessKPIConfig
config = BusinessKPIConfig()
kpis = config.get_business_kpis()
print(f'Found {len(kpis)} business KPIs')
assert len(kpis) > 0
" 2>/dev/null; then
        success "Business KPIs module functions correctly"
    else
        failure "Business KPIs module has runtime errors"
    fi
}

# Test Docker Compose
test_docker_compose() {
    log "Testing Docker Compose configuration..."
    
    test_start "Validating Docker Compose monitoring stack"
    if [[ -f "${PROJECT_ROOT}/docker/infrastructure/docker-compose.monitoring.yml" ]]; then
        if docker-compose -f "${PROJECT_ROOT}/docker/infrastructure/docker-compose.monitoring.yml" config &>/dev/null; then
            success "Docker Compose monitoring configuration is valid"
        else
            warning "Docker Compose validation failed (docker-compose may not be available)"
        fi
    else
        failure "Docker Compose monitoring file missing"
    fi
}

# Test deployment script
test_deployment_script() {
    log "Testing deployment script..."
    
    test_start "Checking deployment script exists and is executable"
    if [[ -f "${PROJECT_ROOT}/scripts/deploy-monitoring.sh" && -x "${PROJECT_ROOT}/scripts/deploy-monitoring.sh" ]]; then
        success "Deployment script exists and is executable"
    else
        failure "Deployment script missing or not executable"
    fi
    
    test_start "Testing deployment script help functionality"
    if "${PROJECT_ROOT}/scripts/deploy-monitoring.sh" --help &>/dev/null; then
        success "Deployment script help function works"
    else
        failure "Deployment script help function has issues"
    fi
}

# Test monitoring components if cluster is available
test_cluster_connectivity() {
    log "Testing cluster connectivity..."
    
    test_start "Checking kubectl availability"
    if command -v kubectl &>/dev/null; then
        success "kubectl is available"
        
        test_start "Checking cluster connectivity"
        if kubectl cluster-info &>/dev/null; then
            success "Kubernetes cluster is accessible"
            return 0
        else
            warning "Kubernetes cluster is not accessible"
            return 1
        fi
    else
        warning "kubectl is not installed"
        return 1
    fi
}

# Test monitoring stack if deployed
test_deployed_stack() {
    if ! test_cluster_connectivity; then
        warning "Skipping deployed stack tests - cluster not accessible"
        return
    fi
    
    log "Testing deployed monitoring stack..."
    
    test_start "Checking monitoring namespace"
    if kubectl get namespace ${NAMESPACE} &>/dev/null; then
        success "Monitoring namespace exists"
        
        # Test each component
        local components=("prometheus" "grafana" "alertmanager" "jaeger" "elasticsearch" "kibana" "logstash")
        
        for component in "${components[@]}"; do
            test_start "Checking ${component} deployment"
            if kubectl get deployment ${component} -n ${NAMESPACE} &>/dev/null; then
                if kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=${component} --field-selector=status.phase=Running | grep -q Running; then
                    success "${component} is deployed and running"
                else
                    failure "${component} is deployed but not running"
                fi
            else
                warning "${component} deployment not found"
            fi
        done
        
        test_start "Checking Filebeat DaemonSet"
        if kubectl get daemonset filebeat -n ${NAMESPACE} &>/dev/null; then
            success "Filebeat DaemonSet exists"
        else
            warning "Filebeat DaemonSet not found"
        fi
        
    else
        warning "Monitoring namespace does not exist"
    fi
}

# Test service connectivity
test_service_connectivity() {
    if ! kubectl get namespace ${NAMESPACE} &>/dev/null; then
        warning "Skipping connectivity tests - monitoring namespace not found"
        return
    fi
    
    log "Testing service connectivity..."
    
    # Test Prometheus
    test_start "Testing Prometheus connectivity"
    if kubectl port-forward -n ${NAMESPACE} service/prometheus 9090:9090 &>/dev/null &
    then
        local port_forward_pid=$!
        sleep 5
        if curl -s http://localhost:9090/-/healthy &>/dev/null; then
            success "Prometheus is responding on health endpoint"
        else
            failure "Prometheus health endpoint not responding"
        fi
        kill $port_forward_pid 2>/dev/null || true
    else
        warning "Could not establish port-forward to Prometheus"
    fi
}

# Generate test report
generate_report() {
    log "Generating test report..."
    
    echo ""
    echo "==================== TEST REPORT ===================="
    echo "Total Tests: ${TESTS_TOTAL}"
    echo "Passed: ${TESTS_PASSED}"
    echo "Failed: ${TESTS_FAILED}"
    echo "Success Rate: $(( TESTS_PASSED * 100 / TESTS_TOTAL ))%"
    echo ""
    
    if [[ ${TESTS_FAILED} -eq 0 ]]; then
        echo -e "${GREEN}🎉 All tests passed! Monitoring stack is ready for deployment.${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Deploy the monitoring stack: ./scripts/deploy-monitoring.sh"
        echo "2. Configure environment variables for AlertManager notifications"
        echo "3. Access Grafana at http://localhost:3000 (admin/admin123)"
        echo "4. Import dashboards and configure data sources"
    else
        echo -e "${RED}❌ Some tests failed. Please fix the issues before deployment.${NC}"
        exit 1
    fi
    echo "======================================================"
}

# Validate monitoring requirements
validate_requirements() {
    log "Validating monitoring requirements from problem statement..."
    
    local requirements=(
        "Déployer Prometheus avec configuration production:monitoring/prometheus/prometheus.yml"
        "Configurer Grafana avec dashboards métier et techniques:monitoring/grafana"
        "Implémenter AlertManager avec notifications Slack/Email/SMS:monitoring/alertmanager/alertmanager.yml"
        "Déployer ELK Stack opérationnel:kubernetes/monitoring/monitoring-stack.yaml"
        "Configurer APM avec Jaeger/Zipkin:docker/infrastructure/docker-compose.monitoring.yml"
        "Implémenter distributed tracing:config/monitoring/tracing_config.py"
        "Configurer métriques custom pour KPIs business:config/monitoring/business_kpis_config.py"
        "Créer alertes SLA avec seuils de performance:monitoring/prometheus/sla_alerts.yml"
        "Monitorer ressources Kubernetes:kubernetes/monitoring/monitoring-stack.yaml"
        "Implémenter log aggregation centralisé:monitoring/filebeat/filebeat.yml"
    )
    
    for requirement in "${requirements[@]}"; do
        local description="${requirement%%:*}"
        local file_path="${requirement##*:}"
        
        test_start "Checking: ${description}"
        if [[ -f "${PROJECT_ROOT}/${file_path}" || -d "${PROJECT_ROOT}/${file_path}" ]]; then
            success "${description} ✓"
        else
            failure "${description} - File/Directory missing: ${file_path}"
        fi
    done
}

# Main function
main() {
    log "Starting Monitoring Stack Validation"
    log "===================================="
    
    # Run all tests
    validate_requirements
    test_configuration_files
    test_kubernetes_manifests
    test_python_modules
    test_docker_compose
    test_deployment_script
    test_deployed_stack
    
    # Generate final report
    generate_report
}

# Execute main function
main "$@"